buildup:
	docker-compose up --build

alembic:
	docker-compose exec fastapi-app alembic revision --autogenerate -m "init migration"
	docker-compose exec fastapi-app alembic upgrade head

connect_db:
	docker-compose exec postgres psql -U se_test_user streamenergy_test