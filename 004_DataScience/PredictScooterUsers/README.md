This was the first complete machine learning project I did independently in early 2020. Was rather badly done because I misunderstood the features to be predicted. Nevertheless, it was an excellent learning experience because I received useful feedback from data science practitioners and also realised that some of my old ways of coding were not the most optimal.


# This Machine Learning Pipeline is developed with these purposes: #
- To import the E-Scooter dataset as a pandas dataframe
- To perform data cleaning and preprocessing based on findings from the Exploratory Data Analysis
- To build a basic machine learning model
- To use the machine learning model to predict the E-Scooter count based on the other attribues from the dataset

# The MLP is designed with these components: #
- Main.py: this is the main and the only script to be executed. It contains the skeleton of the MLP and the key steps to be performed.
- ModelConfig.py: this script is for users to configure the choice of Machine Learning models and other parameters. It will be read by the main script.
- modelFunctions.py: this script contains customized functions written for this MLP.
- getInputData.py: this script contains a function to import the dataset and pass it to the main script as pandas dataframe, also the answer to Part 1 of this assessment.
- 'run.sh': the executable bash script that will install the required libraries and execute the main script.

# The model chosen for this exercise is: #
- Supervised machine learning: In this example we have a target variable in mind -- 'guest_scooters' -- and we are aiming to predict this value with other attributes. Supervised machine learning allows us to train the model with data already 'labeled' with the correct answer to predict unforeseen data. Since we are not looking for patterns in data, supervised machine learning is more suitable for our purpose.
- Linear Regression model: the target feature, guest_scooter, is a continuous numeric variable. Regression model will allow us to generate similar continous numeric variable.


# Evaluation of the model: #
- By using 50-fold cross validation, the result ranges between 0.35 to 0.52.
- By using 0.1 of data as test data and random_state of 120, the score fluctuates around 0.4.
- Overall, the model accuracy is less than 50%. The accuracy is not as satisfactory as expected. It could be attributed to the high variability of results as observed from EDA, even when the explanatory variables are similar. 

# How to configure this model: #
1. Open the ModelConfig.py in the editor, and amend the parameters as deemed appropriate:
-- crossValConfig: parameters for cross-validation
-- OutputConfig: parameters for metrics output (saved as txt file)
-- predictorSelector: model set-up for prediction
-- preprocessorSelector: model set-up for preprocessing
-- splitRatioConfig: parameters for setting aside test/train dataset
2. Execute main.py

# How to customize this model: #
1. Customize data input --> look for getInputData.py and change the database details accordingly
2. Customize data cleaning process --> look for modelFunctions.py and amend the cleanData function