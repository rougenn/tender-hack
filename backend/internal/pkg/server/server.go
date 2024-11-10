package server

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func (r *Server) newAPI() *gin.Engine {
	engine := gin.New()
	r.logger.Info("new api", zap.String("host", r.host))

	// Добавьте поддержку CORS
	engine.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:8090"}, // Разрешенные домены
		AllowMethods:     []string{"GET", "POST", "OPTIONS"},
		AllowHeaders:     []string{"Content-Type", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
	}))

	// API маршруты
	engine.GET("/health", func(ctx *gin.Context) {
		r.logger.Info("request", zap.String("endpoint", "/health"))
		ctx.Status(http.StatusOK)
	})
	engine.POST("/analyze-links", r.AnalyzeLinks)

	// Путь к статическим файлам
	absPath := "/home/user/projects/tender-hack/frontend" // Замените на свой путь
	fmt.Printf("Serving static files from: %s\n", absPath)

	engine.Static("/static", absPath)

	return engine
}

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

type requestUrls struct {
	Urls []string `json:"urls"`
}

func (r *Server) AnalyzeLinks(ctx *gin.Context) {
	var requestBody requestUrls

	// Прочитать JSON от клиента
	if err := ctx.ShouldBindJSON(&requestBody); err != nil {
		r.logger.Error("can't bind JSON", zap.Error(err))
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Отправить запрос на FastAPI
	fastApiUrl := "http://127.0.0.1:8000/process-urls" // Адрес вашего FastAPI
	requestBodyBytes, err := json.Marshal(requestBody)
	if err != nil {
		r.logger.Error("can't marshal request", zap.Error(err))
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Internal Server Error"})
		return
	}

	resp, err := http.Post(fastApiUrl, "application/json", bytes.NewBuffer(requestBodyBytes))
	if err != nil {
		r.logger.Error("error sending request to FastAPI", zap.Error(err))
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Internal Server Error"})
		return
	}
	defer resp.Body.Close()

	// Чтение ответа от FastAPI
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		r.logger.Error("error reading FastAPI response", zap.Error(err))
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Internal Server Error"})
		return
	}

	if resp.StatusCode != http.StatusOK {
		r.logger.Error("FastAPI returned error", zap.String("response", string(body)))
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Error from FastAPI"})
		return
	}

	// Вернуть результат клиенту
	fmt.Println(string(body))
	ctx.Data(http.StatusOK, "application/json", body)
}

func (r *Server) Start() {
	err := r.newAPI().Run(r.host)
	if err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
