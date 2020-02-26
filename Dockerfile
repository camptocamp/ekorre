FROM python:3

WORKDIR /app

COPY . .

RUN make deps && make install

USER 1000

ENTRYPOINT ["ekorre"]
CMD [""]
