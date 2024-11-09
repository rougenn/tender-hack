package server

import (
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

	engine.GET("/health", func(ctx *gin.Context) {
		r.logger.Info("request", zap.String("endpoint", "/health"))
		ctx.Status(http.StatusOK)
	})

	engine.POST("/analyze-links", r.AnalyzeLinks)

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

	// make request to script api and get request
	// ctx.json или csv

	ctx.Status(http.StatusOK)
}

func (r *Server) Start() {
	err := r.newAPI().Run(r.host)
	if err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
