CREATE DATABASE linked_in_spider;
USE linked_in_spider;

CREATE TABLE job (
    id BIGINT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    date DATE NOT NULL,
    salary DECIMAL(10, 2),
    job_type ENUM('OnSite', 'Remote', 'Hybrid', 'Unknown') NOT NULL,
    location VARCHAR(255) NOT NULL
);

CREATE TABLE job_seniority (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    job_id BIGINT NOT NULL REFERENCES job(id),
    name ENUM('Internship', 'Junior', 'Associate', 'Senior', 'Director', 'Executive', 'Unknown') NOT NULL
);

CREATE TABLE skill (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE job_skill (
    job_id BIGINT NOT NULL REFERENCES job(id),
    skill_id BIGINT NOT NULL REFERENCES skill(id),
    PRIMARY KEY (job_id, skill_id)
);

INSERT INTO skill (name) VALUES ('Power BI');
INSERT INTO skill (name) VALUES ('Python');
INSERT INTO skill (name) VALUES ('Tableau');
INSERT INTO skill (name) VALUES ('SQL');
INSERT INTO skill (name) VALUES ('Excel');
INSERT INTO skill (name) VALUES ('Big Query');
INSERT INTO skill (name) VALUES ('Google Analytics');
INSERT INTO skill (name) VALUES ('Data Warehouse');
INSERT INTO skill (name) VALUES ('Data lake');
