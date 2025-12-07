create table University (
	univ_id CHAR(20) primary key,
	univ_name VARCHAR(100)
);

create table Category (
	category_id INT primary key,
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
	subject_id CHAR(20) references Subject(subject_id),
	exam_year CHAR(20) references ExamYear(exam_year),
	level INT,
	percentile DECIMAL(5,2),
	min_score_range DECIMAL(5,2), 
	max_score_range DECIMAL(5,2)
);

