# -*- coding: utf-8 -*- 
#!/usr/bin/env python

import os
import sys
import time
import signal
import socket
import httplib
import optparse
import logging
import threading
import fcntl
#import traceback

monitor_name = 'monitor'
content_server_proc = None
server_proc_dict = {}

g_self_name = sys.argv[0]
g_is_child = False

check_status_timer = None
check_interval = 60.0
req_timeout = 6

f_lock = None

shuting_down = False

class ServerProc:
  def __init__(self, exe_bin, port):
    self.pid = -1
    self.exe_bin = exe_bin
    self.port = port

  def get_cmd_args(self):
    args = []
    args.append(self.exe_bin)
    args.append('--port')
    args.append(str(self.port))
    return args

def create_optparse():
  """
  @return: Obj(OptionParser)
  """
  self_name = sys.argv[0]
  opt_parser = optparse.OptionParser(usage="python %s [options]" % (self_name), version="%s 1.0" % (self_name))
  opt_parser.add_option("--exec_bin", action="store", dest="exec_bin", type="string", \
                        help="exe file of the server program.")
  opt_parser.add_option("--log_file", action="store", dest="log_file", type="string", \
                          help="log file path for this server monitor.")
  opt_parser.add_option("--port_begin", action="store", dest="port_begin", type="int", \
                        help="the listening port of this server")
  opt_parser.add_option("--proc_count", action="store", dest="proc_count", type="int", \
                        help="the listening port of this server")
  opt_parser.add_option("--debug", action="store_true", dest="debug", default=False, \
                          help="using debug model.")

  return opt_parser

def init_logger(opt):
  global logger


  if not opt.log_file:
    sys.stderr.write("init_logger error: illegal log file\n")
    sys.exit(-1)

  log_handler = logging.FileHandler(opt.log_file)
  formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
  log_handler.setFormatter(formatter)
  logger = logging.getLogger("")
  logger.addHandler(log_handler)

  if opt.debug:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)

def request_timeout(server_proc):
  timed_out = False
  conn = None
  try:
    register_path = "/hello"
    conn = httplib.HTTPConnection("127.0.0.1", server_proc.port, timeout=req_timeout)
    conn.request('GET', register_path, '', {'Connection' : 'close'})
    response = conn.getresponse()
  except socket.timeout:
    timed_out = True
  finally:
    if conn:
       conn.close()
  return timed_out

def check_server_procs():
  """
  check status for running servers
  """
  global check_status_timer
  global server_proc_dict

  for pid, server_proc in server_proc_dict.items():
    try:
      timed_out = request_timeout(server_proc)
      logger.debug("checking port %s, timed_out=%s" % (server_proc.port, timed_out))
      if timed_out:
        logger.info("request timed out, killing: port=%s, pid=%s" % (server_proc.port, server_proc.pid))
        os.kill(server_proc.pid, signal.SIGTERM)
    except:
      #traceback.print_exc()
      pass
  check_status_timer = threading.Timer(check_interval, check_server_procs)
  check_status_timer.start()

def shutdown(msg=''):
  global shuting_down
  global server_proc_dict

  shuting_down = True
  logger.info("going to shutdown, %s" % msg)
  for pid, server_proc in server_proc_dict.items():
    try:
        os.kill(pid, signal.SIGTERM)
        if pid != server_proc.pid:
          logger.info("port=%s: pid not match!" % server_proc.port)
          os.kill(server_proc.pid, signal.SIGTERM)
        logger.debug("port=%s`pid=%s`msg=stoped" % (server_proc.port, server_proc.pid))
    except Exception, e:
      logger.debug("port=%s`pid=%s`msg=error:%s" % (server_proc.port, server_proc.pid, str(e)))


def handle_sigterm(signum, frame):
  global g_is_child
  if not g_is_child:
    shutdown()

def process_lock(pid_file):
  global f_lock

  ret = 0
  f_lock = file(pid_file, 'a+')
  try:
    fcntl.flock(f_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
  except:
    ret = -1
  return ret

def process_unlock():
  if f_lock != None:
    fcntl.flock(f_lock, fcntl.LOCK_UN)

def read_pid_file(pid_file):
  pid = -1
  if os.path.exists(pid_file):
    try:
      pid = int(file(pid_file).read().strip())
    except:
      #print "WARNING - pid file %s is invalid" % (pidfile)
      pid = -1
  else:
    #print "WARNING - pid file %s isn't exists" % (pidfile)
    pid = -1
  return pid

def write_pid_file(pid_file, pid):
  abspath = os.path.abspath(pid_file)
  dirname = os.path.dirname(abspath)
  if not os.path.exists(dirname):
    os.makedirs(dirname, 0775)
  file(pid_file, "w").write("%s" % pid)

def start_server_proc(server_proc):
  global server_proc_dict
  logger.debug("starting server process: port=%s" % server_proc.port)
  pid = os.fork()
  if pid > 0:
    server_proc.pid = pid
    server_proc_dict[pid] = server_proc
    logger.info("port=%s`pid=%d`msg=proc_started" % (server_proc.port, pid))
  elif pid < 0:
    sys.exit(-1)
  else:
    exec_cmd = ''
    try:
      cmd_args = server_proc.get_cmd_args()
      exec_cmd = ' '.join(cmd_args)
      logger.debug('try to exec cmd: %s' % exec_cmd)
      os.execvp(server_proc.exe_bin, cmd_args)
    except Exception, e:
      logger.error('failed to start server process, args=%s, cmd=%s, error=%s' % (cmd_args, exec_cmd, str(e)))
      sys.exit(-1)
    sys.exit(0)

def daemonize(opt):
  try:
    pid = os.fork()
    if pid > 0:
      sys.exit(0)
  except OSError, e:
    sys.stderr.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
    sys.exit(1)

  os.setsid()
  os.umask(0)

  try:
    pid = os.fork()
    if pid > 0:
      sys.exit(0)
  except OSError, e:
    sys.stderr.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
    sys.exit(1)

  sys.stdout.flush()
  sys.stderr.flush()

  si = file("/dev/null", 'r')
  so = file("/dev/null", 'a+')

  os.dup2(si.fileno(), sys.stdin.fileno())
  os.dup2(so.fileno(), sys.stdout.fileno())

def main():
  global g_is_child
  global g_self_name
  global shuting_down
  global server_proc_dict

  opt_parser = create_optparse()
  opt, args = opt_parser.parse_args()


  daemonize(opt)

  init_logger(opt)

  logger.info("can't find executable file:.")

  exe_bin = opt.exec_bin
  if not exe_bin or not os.path.exists(exe_bin):
    logger.debug("can't find executable file: path = %s." % (exe_bin))
    sys.exit(1)

  try:
    port = int(opt.port_begin)
    if not port or port <= 0 or port >= 65535:
      logger.debug("specify a valid port, current port = %s." % (port))
      sys.exit(-1)
    proc_count = int(opt.proc_count)
  except Exception, e:
    logger.debug("command line format error: %s." % str(e))
    sys.exit(-1)

  # listen port range: [server_port_begin, ..., server_port_begin + server_proc_count]
  server_port_begin = port
  server_proc_count = proc_count

  signal.signal(signal.SIGTERM, handle_sigterm)
  signal.signal(signal.SIGINT, handle_sigterm)

  pid_file = "../var/%s.pid" % monitor_name
  nlock = process_lock(pid_file)
  if nlock == -1:
    logger.debug("%s@%s is already running, pid is %d." % \
                 (g_self_name, monitor_name, read_pid_file(pid_file)))
    os._exit(0)

  pid = os.getpid()
  write_pid_file(pid_file, pid)

  logger.info("monitor started, pid=%s, port_begin=%d, proc_count=%d "% \
          (pid, server_port_begin, server_proc_count))

  try:
    for port in range(server_port_begin, server_port_begin + server_proc_count):
      server_proc = ServerProc(exe_bin, port)
      start_server_proc(server_proc)
  except Exception, e:
    sys.stderr.write(str(e))
    shutdown(str(e))
    os._exit(-1)

  global check_status_timer
  check_status_timer = threading.Timer(check_interval, check_server_procs)
  check_status_timer.start()

  error_msg = ''
  while shuting_down == False:
    try:
      npid, ret = os.wait()
      if ret == 0xFF00 or ret == 9 or shuting_down == True:
        # -1 子进程启动错误就不再派生子进程了
        break
      server_proc = server_proc_dict.pop(npid)
      logger.info("server proc exit[pid=%s, port=%s, ret=%s], restart now" % \
              (npid, server_proc.port, ret))
      server_proc.pid = -1
      start_server_proc(server_proc)
    except Exception, e:
      sys.stderr.write(str(e))
      logger.error("loop err: %s" % str(e))
      #traceback.print_exc()
      break

  if shuting_down == False:
    shutdown(error_msg)
  os._exit(0)
      
if __name__=="__main__":
  main()
