# Tablero de Lotes y Culticos

<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">

![image](assets/datalab.png)

  </a>

  <p align="center">
      This microservice generates a summary dashboard of Fields and Crops data uploaded to 360, developed with Streamlit and Python <br />
    <br />
    <br />
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#arquitechture-diagram">Arquitechture-Diagram</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#usage">Usage</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->

## About the Project

This microservice generates a summary dashboard of Fields and Crops data uploaded to 360, based on the selected Domain, Area(s), Workspace(s), Season(s), and Farm(s), Crop(s) and Hybrids / Varieties.

It consists of __ sections:

1. Upper Section: This section includes the Domain logo, the dashboard title, a language selector, and user information.

2. Filters (Sidebar): Users can filter data according to Domain, Area(s), Workspace(s), Campaign(s), Establishment(s), Crop(s), and Hybrid(s)/Variety(ies). An option to "select all" is available for all categories. By default, Crops and Hybrids/Varieties are included in this selection.

3. Metrics: Located below the Upper Section, this section displays metrics relevant to the selected filters, such as:

    * Farms
    * Field
    * Hectares
    * Crops
    * Hybrids / Varieties
    * Fields without crops
    * Fields without hybrids/varieties
    * Fields without sowing date


## Arquitechture Diagram 

![datarequest](https://github.com/GeoagrobyTEK/ms-datarequest/assets/101668748/deb86ec8-e2c3-42f6-9d20-8eb59b8983ce)

### Description

   
1- The user must login in 360.geoagro.com.

2- In the switcher (up-left corner) must select "Data Request".

4- It opens the url with two tokens, token1 has an info of user like:
   
     user_info={'email': user_email, 'language': 'es', 'env': 'prod', 'domainId': None, 'areaId': None,   'workspaceId': None, 'seasonId': None, 'farmId': None}

5- An Application Load Balancer take the request and send to fargate.
  
6- In fargate, the datarequest form is running troughby docker as service.
   


<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With
* [![Python][Python.org]][Python-url]
* [![docker][docker]][docker-url]
* [![streamlit][streamlit]][streamlit-url]
* [![plotly][plotly]][plotly-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/GeoagrobyTEK/ms-datarequest.git
   ```
2. Install dependencies
   ```sh
     pip3 install -r requirements.txt
   ```
3. Execute
   ```sh
     streamlit python3 app.py 
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Usage

Uncomment lines 1003 to 1005 and Comment lines 1008 to 1032.
In this way, the app runs with info presetted in user_info (Please, use your email).

Run:
 ```sh
    http://localhost:5000/
 ```
  
<!-- ROADMAP -->
## Roadmap

<a href="https://docs.google.com/document/d/1QxpfWqW6_ozwE6CJHmlvxza1wv9uV7N08ZcqytdeTwc/edit#heading=h.yq8ikg4wx1f9">
  COM-108 Análisis Escenario 1 - pedido de procesamiento de rindes y otros servicios
</a>
<p><a href="#readme-top">back to top</a></p>

<!-- CONTACT -->
## Contact

Adrian Cuello - [Adrian Cuello](mailto:acuello@geoagro.com.com?subject=[GitHub]ms-collector)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[product-screenshot]: images/screenshot.png

[Python.org]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://python.org/

[streamlit]: https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white
[streamlit-URL]: https://docs.streamlit.io/

[docker]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[docker-URL]: https://www.docker.com/

[plotly]: https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white
[plotly-url]: https://plotly.com/python/
