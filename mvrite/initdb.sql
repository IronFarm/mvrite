USE mvrite;

CREATE TABLE IF NOT EXISTS listings (
    id              BIGINT,
    title           VARCHAR(255),
    location_string VARCHAR(255),
    estate_agent    VARCHAR(255),
    added           TIMESTAMP,
    status_date     TIMESTAMP,
    status_keyword  VARCHAR(16),
    price           BIGINT,
    latitude        FLOAT,
    longitude       FLOAT
);
