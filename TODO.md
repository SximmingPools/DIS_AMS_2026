# Exercise Sheet 1 TODO

## Team

- [x] Form a team of 2 or 3 people.
- [x] Create or join the team in Moodle under `Demo Teams`.

## Local Setup

- [ ] Install and start PostgreSQL locally.
- [ ] Create a persistent PostgreSQL database for the exercise.
- [ ] Create a Python virtual environment.
- [ ] Install the Python dependencies from `requirements.txt`.
- [ ] Configure `DATABASE_URL` in `.env`.
- [ ] Verify Python can connect to PostgreSQL.
- [ ] Confirm PostgreSQL supports a defined transaction isolation level.
- [ ] Confirm multiple Python clients can connect to the same database.
- [ ] Confirm transactions can be started, committed, and rolled back.
- [ ] Confirm CSV data can be imported into PostgreSQL.

## Transaction Experiment

- [ ] Open connection A to the persistent database without using a GUI.
- [ ] Create a table through connection A.
- [ ] Insert the first tuple through connection A.
- [ ] Keep connection A open.
- [ ] Open connection B to the same database.
- [ ] Start one transaction in connection A.
- [ ] Start one transaction in connection B.
- [ ] Insert a new record through connection A.
- [ ] Insert a different new record through connection B.
- [ ] Query the table contents through connection A.
- [ ] Query the table contents through connection B.
- [ ] Commit the transaction in connection A.
- [ ] Commit the transaction in connection B.
- [ ] After each successful commit, query the table contents again from the successful connection.
- [ ] If both commits succeed, open connection C and query the table contents.
- [ ] Start a new transaction in connection A.
- [ ] Start a new transaction in connection B.
- [ ] Update the original record through connection A.
- [ ] Update the same original record to a different value through connection B.
- [ ] Commit the update transaction in connection A.
- [ ] Commit the update transaction in connection B.
- [ ] After each successful update commit, query the table contents again from the successful connection.
- [ ] If both update commits succeed, open connection C and query the table contents.
- [ ] Save notes after every executed transaction step.

## Coffee Sales CSV

- [x] Download the `Coffee Sales` CSV dataset from Moodle.
- [x] Start with a fresh database for the CSV import task.
- [x] Inspect the CSV columns and sample values in `src/db_exercise/operations-1-c.py`.
- [x] Identify useful table constraints not provided by the CSV file.
- [x] Decide column data types for the Coffee Sales table.
- [x] Create a table for the Coffee Sales data.
- [x] Import the CSV into the table as automatically as possible.
- [x] Query the table to verify the imported data is present.
- [x] Add the identified constraints to the Coffee Sales table.
- [x] Add a primary key column if the CSV does not provide one.
- [x] Check whether the Coffee Sales table contains redundant information.
- [x] If redundant information exists, move it into separate normalized tables.
- [x] Define foreign key relations for normalized tables.

## Final

- [ ] Commit the final source code and notes before answering the questionnaire.

