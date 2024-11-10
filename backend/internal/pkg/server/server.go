package server

import (
	"fmt"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

type Server struct {
	host   string
	logger *zap.Logger
}

func New(host string) *Server {
	logger, _ := zap.NewProduction()
	s := &Server{
		host:   host,
		logger: logger,
	}

	return s
}

func (r *Server) newAPI() *gin.Engine {
	engine := gin.New()
	r.logger.Info("new api", zap.String("host", r.host))

	// API маршруты
	engine.GET("/health", func(ctx *gin.Context) {
		r.logger.Info("request", zap.String("endpoint", "/health"))
		ctx.Status(http.StatusOK)
	})
	engine.POST("/analyze-links", r.AnalyzeLinks)

	// Абсолютный путь к папке frontend
	absPath := "/home/user/projects/tender-hack/frontend" // замените на полный путь к папке `frontend`
	fmt.Printf("Serving static files from: %s\n", absPath)

	engine.Static("/static", absPath)

	return engine
}

type requestUrls struct {
	Urls []string `json:"urls"`
}

func (r *Server) AnalyzeLinks(ctx *gin.Context) {
	var requestBody requestUrls

	if err := ctx.ShouldBindJSON(&requestBody); err != nil {
		r.logger.Error("cant bind json")
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	r.logger.Info("got links", zap.Strings("urls", requestBody.Urls))

	// Здесь вы можете вызвать скрипт для анализа ссылок или выполнить необходимую логику.
	ctx.JSON(http.StatusOK, gin.H{"success": true})
}

func (r *Server) Start() {
	err := r.newAPI().Run(r.host)
	if err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
