package main

import (
	"github.com/gin-gonic/gin"
	_ "go-gin/modules/log" // 日志
	// _ "go-gin/modules/schedule" // 定时任务
	"runtime"
	"go-gin/config"
	"go-gin/modules/server"
	"go-gin/routers"
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
