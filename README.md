<p align="center"><img src="https://github.com/nathanbronson/LinearSDFModel/blob/main/logo.jpg?raw=true" alt="logo" width="200"/></p>

_____
# LinearSDFModel
estimating a linear model of the stochastic discount factor

## About
LinearSDFModel is a project estimating a linear model of the stochastic discount factor (SDF) using data from a small universe of real estate companies. The model uses the relationship between the SDF and the tangent portfolio to estimate the model in terms of company characteristics. Using the property that the expected value of the product of the SDF and excess returns for a given period is zero, we create a mispricing error. We use this mispricing error as a loss function with which we optimize the parameters of the linear model using gradient descent.

## Usage
All code to generate results and visualizations from the report can be found in `project.ipynb`. Data is not included.

## License
See `LICENSE`.

## Report
![page1](./images/report%20page%201.png)
![page2](./images/report%20page%202.png)
![page3](./images/report%20page%203.png)
![page4](./images/report%20page%204.png)
![page5](./images/report%20page%205.png)
![page6](./images/report%20page%206.png)
