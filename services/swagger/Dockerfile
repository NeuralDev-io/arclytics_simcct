# Looking for information on environment variables?
# We don't declare them here — take a look at our docs.
# https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/configuration.md

FROM nginx:1.16-alpine

LABEL maintainer="Andrew Che <andrew@neuraldev.io>"

RUN apk --no-cache add nodejs

ENV API_KEY "**None**"
ENV SWAGGER_JSON "/app/swagger.yaml"
ENV PORT 8080
ENV BASE_URL ""

COPY ./docker/nginx.conf ./docker/cors.conf /etc/nginx/

# copy swagger files to the `/js` folder
COPY ./dist/* /usr/share/nginx/html/
COPY ./docker/run.sh /usr/share/nginx/
COPY ./docker/configurator /usr/share/nginx/configurator

COPY ./swagger.yaml /usr/share/nginx/html/swagger.yaml

RUN chmod +x /usr/share/nginx/run.sh

EXPOSE 3001

CMD ["sh", "/usr/share/nginx/run.sh"]
