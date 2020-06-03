DROP TABLE IF EXISTS response;
DROP TABLE IF EXISTS response_header;

CREATE TABLE response (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL,
    body TEXT NOT NULL,
    content_type TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    expires TIMESTAMP,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE response_header (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  response_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  value TEXT NOT NULL,
  FOREIGN KEY (response_id) REFERENCES response (id)
);