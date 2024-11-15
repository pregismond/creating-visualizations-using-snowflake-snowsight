# Visualizing Car Sales and Dealer Profits Using Snowflake Snowsight

![Visitors](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgithub.com%2Fpregismond%2Fcreating-visualizations-using-snowflake-snowsight&label=Visitors&countColor=%230d76a8&style=flat&labelStyle=none)
[![License](https://img.shields.io/badge/License-Apache_2.0-0D76A8?style=flat)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10.12](https://img.shields.io/badge/Python-3.10.12-green.svg)](https://shields.io/)
[![Snowflake 8.41.2](https://img.shields.io/badge/Snowflake-8.41.2-green?style=flat&logo=snowflake&logoColor=white)](https://shields.io/)

## Disclaimer

This repository contains a project based on the final assignment for the **[BI Dashboards with IBM Cognos Analytics and Google Looker](https://www.coursera.org/learn/bi-dashboards-with-ibm-cognos-analytics-and-google-looker)** course on Coursera. The original assignment focused on creating and analyzing business intelligence (BI) dashboards/reports using IBM Cognos Analytics and Google Looker Studio.

For this project, I have adapted the assignment to utilize Snowflake's Snowsight. Additionally, I have provided a Streamlit app that produces the same visualizations using Streamlit-in-Snowflake (SiS).

### Usage

* You are welcome to use this repository as a reference or starting point for your own project.

* If you choose to fork this repository, please ensure that you comply with the terms of the Apache License and give proper credit to the original authors.

## Project Scenario

SwiftAuto Traders has hired a data scientist to analyze car sales and profits for each dealer. Their first task is to create visualizations and present them as a dashboard to the regional manager.

## Objectives

* Analyze the historical trends in car sales for SwiftAuto Traders
* Provide insights on car sales and profits for each dealer

## Datasets

For this project, we will use a modified subset of the [Automotive Industry Sample Data](./Automotive_Industry/), which is available in this repository.

The original dataset can be found here: [Automotive Industry Sample Data](https://accelerator.ca.analytics.ibm.com/bi/?utm_source=skills_network&utm_content=in_lab_content_link&utm_id=Lab-IBMSkillsNetwork-DV0130EN-Coursera&perspective=authoring&pathRef=.public_folders%2FIBM%2BAccelerator%2BCatalog%2FContent%2FDAT00142&id=i22898C2A4DD748F79E0FC2BD017F4FE8&objRef=i22898C2A4DD748F79E0FC2BD017F4FE8&action=run&format=HTML&cmPropStr=%7B%22id%22%3A%22i22898C2A4DD748F79E0FC2BD017F4FE8%22%2C%22type%22%3A%22reportView%22%2C%22defaultName%22%3A%22DAT00142%22%2C%22permissions%22%3A%5B%22execute%22%2C%22read%22%2C%22traverse%22%5D%7D)

The terms of use are located at https://developer.ibm.com/terms/ibm-developer-terms-of-use/.

## Task Information
**Task 1**: Create a dashboard titled as `Sales` to capture the following KPI metrics:
* Capture Profit (formatted to 1 decimal place in millions of US dollars)
* Capture Quantity sold
* Create a bar chart to capture Quantity sold by model
* Capture Average quantity sold

**Task 2**: Develop a column chart to display Profit by Dealer ID in the `Sales` dashboard sorted in ascending order.

**Task 3**: Create another dashboard titled as `Service` and capture the following KPI metrics as visualizations:
* Create a column chart to capture the number of recalls per model of car
* Create a treemap to capture the customer sentiment by comparing positive, neutral, and negative reviews.
* Create a line and column chart to capture the quantity of cars sold per month compared to the profit.
* Create a pivot table with heatmap to capture the number of recalls by model and affected system

**Task 4**: Share the dashboards.

## Setup

The [setup_swiftauto_traders.py](./setup_swiftauto_traders.py) Python script has been provided to setup the Snowflake environment for this project. It also handles the uploading of CSV dataset files to stage, creates and loads tables with inferred schemas, and establishes a basic role hierarchy and user setup to demonstrate dashboard sharing within Snowflake.

**Install Snowflake Connector for Python**

Make sure you have Python (version 3.10.12 or later) and `pip` installed on your system. Then, install the required libraries using the provided `requirements.txt` file. The command syntax is:

```bash
python3 -m pip install -r requirements.txt
```

**Set Environment Variables for Snowflake Credentials**

*Bash (Linux/Mac)*
* Open Terminal
* Use the `export` command to set environment variables:
    ```bash
    export SNOWFLAKE_USER='your_username'
    export SNOWFLAKE_PASSWORD='your_password'
    export SNOWFLAKE_ACCOUNT='your_account'
    ```
    Alternatively, you can add the environment variables to your bash login script `.bash_profile` or `.bashrc` so they are automatically set when you log in.

*Windows*
* Open Command Prompt.
* Use the `setx` command to set environment variables:
    ```cmd
    setx SNOWFLAKE_USER "your_username"
    setx SNOWFLAKE_PASSWORD "your_password"
    setx SNOWFLAKE_ACCOUNT "your_account"
    ```
* Restart any open Command Prompt windows for the changes to take effect.

**Execute `setup_swiftauto_traders.py`**

```bash
python3 setup_swiftauto_traders.py
```
Output: [setup_swiftauto_traders.log](./setup_swiftauto_traders.log)

**Final Assignment**

Begin the [Final Assignment using Snowsight](./Final_Assignment_Snowsight.md)<br>
Begin the [Final Assignment using Streamlit-in-Snowsight](./Final_Assignment_Streamlit.md)

## Learner

[Pravin Regismond](https://www.linkedin.com/in/pregismond)

## Acknowledgments

* IBM Skills Network © IBM Corporation 2024. All rights reserved.