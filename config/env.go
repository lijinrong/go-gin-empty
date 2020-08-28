package config

import (
	"flag"
	"fmt"
	"github.com/go-sql-driver/mysql"
	"os"
	"strconv"
)

// 本文件建议在代码协同工具(git/svn等)中忽略
var env = Env{
	Debug: true,

	ServerPort: "4000",

	Database: mysql.Config{
		User:                 "root",
		Passwd:               "123456",
		Addr:                 "127.0.0.1:3306",
		DBName:               "gin-template",
		Collation:            "utf8mb4_unicode_ci",
		Net:                  "tcp",
		AllowNativePasswords: true,
	},
	MaxIdleConns: 50,
	MaxOpenConns: 100,

	RedisIp:       "127.0.0.1",
	RedisPort:     "6379",
	RedisPassword: "",
	RedisDb:       0,

	RedisSessionDb: 1,
	RedisCacheDb:   2,

	AccessLog:     true,
	AccessLogPath: "../storage/logs/access.log",

	ErrorLog:     true,
	ErrorLogPath: "../storage/logs/error.log",

	InfoLog:     true,
	InfoLogPath: "../storage/logs/info.log",

	//APP_SECRET: "YbskZqLNT6TEVLUA9HWdnHmZErypNJpL",
	AppSecret: "YbskZqLNT6TEVLUA9HWdnHmZErypNJpL",
}

func init() {
	mode := os.Getenv("mode")
	if mode == "dev" {
		env.Debug = true
	} else if mode == "prod" {
		env.Debug = false
	}

	var port int
	flag.IntVar(&port, "port", 0, "http listen port")
	flag.Parse()
	fmt.Printf("port %d", port)
	if port != 0 {
		env.ServerPort = strconv.Itoa(port)
	}
}
