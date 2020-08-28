package main

import (
	"github.com/gin-gonic/gin"
	"go-gin/config"
	_ "go-gin/modules/log" // 日志
	"go-gin/modules/server"
	"go-gin/routers"
	// _ "go-gin/modules/schedule" // 定时任务
	"runtime"
)

func main() {
	runtime.GOMAXPROCS(runtime.NumCPU())

	if config.GetEnv().Debug {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	router := routers.InitRouter()

	server.Run(router)
}
