package routers

import (
	"github.com/gin-gonic/gin"
	"go-gin/controllers"
	"go-gin/middleware/auth"
)

func RegisterApiRouter(router *gin.Engine) {

	api := router.Group("/api")
	api.GET("/cookie/set/:userid", controllers.CookieSetExample)
	api.GET("/hello", controllers.Hello)

	// cookie auth middleware
	api.Use(auth.Middleware(auth.CookieAuthDriverKey))
	{
		api.GET("/orm", controllers.OrmExample)
		api.GET("/store", controllers.StoreExample)
		api.GET("/db", controllers.DBExample)
		api.GET("/cookie/get", controllers.CookieGetExample)
	}

	jwtApi := router.Group("/api")
	jwtApi.GET("/jwt/set/:userid", controllers.JwtSetExample)

	// jwt auth middleware
	jwtApi.Use(auth.Middleware(auth.JwtAuthDriverKey))
	{
		jwtApi.GET("/jwt/get", controllers.JwtGetExample)
	}
}
