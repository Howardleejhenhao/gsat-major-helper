create table University (
	univ_id CHAR(3) primary key,
	univ_name VARCHAR(100)
);

create table Category (
	category_id INT primary key,
	academic_cluster VARCHAR(100),
    category_name VARCHAR(100)
);

create table Subject (
	subject_id CHAR(20) primary key,
	subject_name  VARCHAR(50)
);

create table ExamYear (
	exam_year CHAR(20) primary key
);

create table StandardLevel (
	std_id INT primary key,
	exam_year CHAR(20) references ExamYear(exam_year),
	subject_id CHAR(20) references Subject(subject_id),
	top INT,
	high INT,
	avg INT,
	low INT,
	bottom INT
);

create table SubjectPerformance (
	perf_id INT primary key,
	exam_year CHAR(20) references ExamYear(exam_year),
	subject_id CHAR(20) references Subject(subject_id),
	level INT,
	percentile DECIMAL(5,2),
	min_score DECIMAL(5,2), 
	max_score DECIMAL(5,2)
);

create table Department (
    dept_id CHAR(6) primary key,
    univ_id CHAR(3) references University(univ_id),
    dept_name VARCHAR(100),
    category_id INT references Category(category_id)
);

create table AdmissionRecord (
    record_id INT primary key,
    dept_id CHAR(6) references Department(dept_id),
    exam_year CHAR(20) references ExamYear(exam_year),
    has_extra_screen BOOLEAN,
    lowest_total VARCHAR(50)
);

create table SubjectCombination (
    combo_id INT primary key,
    record_id INT references AdmissionRecord(record_id),
    combo_order INT
);

create table CombinationDetail (
    combo_id INT,
    subject_id CHAR(20),
    required_score INT,
    remark VARCHAR(200),
    PRIMARY KEY (combo_id, subject_id),
    FOREIGN KEY (combo_id) REFERENCES SubjectCombination(combo_id),
    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id)
);

create table ExamRequirement (
    req_id INT primary key,
    dept_id CHAR(6) references Department(dept_id),
    exam_year CHAR(20) references ExamYear(exam_year),
    subject_id CHAR(20) references Subject(subject_id),
    required_level VARCHAR(10)
);

CREATE SEQUENCE favorite_sort_order_seq START 1;
CREATE TABLE Favorite (
    favorite_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dept_id CHAR(6) REFERENCES Department(dept_id),
    sort_order INT NOT NULL DEFAULT nextval('favorite_sort_order_seq')
);