package models

import (
	"github.com/jinzhu/gorm"
	"go-gin/config"
	"go-gin/modules/log"
)

var Model *gorm.DB

func init() {
	var err error
	log.Println(config.GetEnv().Database.FormatDSN())
	Model, err = gorm.Open("mysql", config.GetEnv().Database.FormatDSN())

	if err != nil {
		panic(err)
	}
}
