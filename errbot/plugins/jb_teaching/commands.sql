CREATE TABLE courses (
    title TEXT NOT NULL UNIQUE PRIMARY KEY,
    university TEXT NOT NULL
    url TEXT NOT NULL
);

INSERT INTO courses (title, university, url ) VALUES ('Artificial Intelligence', 'National Kaohsiung University of Science and Technology', 'https://ciolh007.github.io/artificial_intelligence/');
