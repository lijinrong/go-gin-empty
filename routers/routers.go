package routers

import (
	"github.com/gin-contrib/pprof"
	"github.com/gin-gonic/gin"
	"go-gin/config"
	"go-gin/middleware"
	"go-gin/middleware/auth"
	"net/http"
	// proxy "github.com/chenhg5/gin-reverseproxy"
)

func InitRouter() *gin.Engine {
	router := gin.New()

	if config.GetEnv().Debug {
		pprof.Register(router) // 性能分析工具
	}

	router.Use(gin.Logger())

	router.Use(handleErrors())            // 错误处理
	router.Use(middleware.RegisterSession()) // 全局session
	router.Use(middleware.RegisterCache())   // 全局cache

	router.Use(auth.RegisterGlobalAuthDriver("cookie", "web_auth")) // 全局auth cookie
	router.Use(auth.RegisterGlobalAuthDriver("jwt", "jwt_auth"))    // 全局auth jwt

	router.NoRoute(func(c *gin.Context) {
		c.JSON(http.StatusNotFound, gin.H{
			"code": 404,
			"msg":  "找不到该路由",
		})
	})

	router.NoMethod(func(c *gin.Context) {
		c.JSON(http.StatusNotFound, gin.H{
			"code": 404,
			"msg":  "找不到该方法",
		})
	})

	RegisterApiRouter(router)

	// ReverseProxy
	// router.Use(proxy.ReverseProxy(map[string] string {
	// 	"localhost:4000" : "localhost:9090",
	// }))

	return router
}
