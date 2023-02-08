ROOT_DIR=${PWD}

.DEFAULT_GOAL := help
.PHONY: build

# tasks
help:
	@echo "Type: make [rule]. Available options are:"
	@echo ""
	@echo "- help"
	@echo "- clean"
	@echo "- format"
	@echo ""
	@echo "- deps"
	@echo "- run-gradio"
	@echo "- run-streamlit"
	@echo ""
	@echo "- docker-build"
	@echo "- docker-run"
	@echo ""
	@echo "- heroku-logs"
	@echo "- heroku-docker-build"

clean:
	@echo "Cleaning..."
	@rm -rf .DS_Store
	@rm -rf *.pyc
	@rm -rf Thumbs.db
	@echo "OK"

deps:
	python3 -m pip install -r requirements.txt

run-gradio:
	python3 app.py

run-streamlit:
	streamlit run app-streamlit.py

docker-build:
	docker build --no-cache -t aichat .

docker-run:
	@echo "Running..."
	@docker run --rm -p 9000:9000 -p 8501:8501 -e SPEECH_KEY=${SPEECH_KEY} -e SPEECH_REGION=${SPEECH_REGION} -e OPENAI_API_KEY=${OPENAI_API_KEY} aichat streamlit run app-streamlit.py

format:
	black .

heroku-logs:
	heroku logs -a aichat --tail

heroku-docker-build:
	heroku container:login
	heroku container:push web -a aichat
	heroku container:release web -a aichat
