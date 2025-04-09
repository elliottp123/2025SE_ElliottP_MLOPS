# Task 2 ML Student performance prediction

## Machine Learning Algorithm

\*\*This is all contained within Task2ML\*\* :

- Data wrangling
- Feature engineering and implementation
- Training
  - Random Forest Classifier
  - Layered Linear Regression
- Visualisation and testing

## webapp implementation

- Python backend
- Javascript front-end server
- API OOP oriented design
- SQL database (for setting new user data)

# Task2ML webapp initialisation

## Initialisation

Prerequisites:

- Python 3.12+
- Flask 3.0.0+
- SQLite 3+
  _(we have this because of codespace)_

1. set up dependancies:

```ruby
pip install -r requirements.txt
```

2. verify .env file:

SECRET_KEY=your-secure-secret-key-here
DATABASE_URL=sqlite:///.databaseFiles/devlog.db

## Task2ML webapp usage

You can do this with API endpoints, but that is out of the scope of this assesment.
run

1. initialise and run the webapp

```ruby
python main.py
```

2. open the forwarded port website

3. put in some data!
   these models work better with females, mathematics, etc.
   There are some fun interactions, like romantic rel can lower predictions, but romantic rel + primary gardian = mother produces a higher prediction.
   But primarily you can get a prediction from data, the end.
   Try and put in some exception case data and see if I missed anything.
