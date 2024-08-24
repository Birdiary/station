# Birdiary - station
Nowadays, more species are threatened with extinction than ever before in the human era.
Especially breeding birds are considered endangered. 
At the same time, it is difficult to obtain sufficient data not only to raise awareness for this situation, but also to gain a better understanding and to develop potential countermeasures.
The Birdiary project demonstrates how a citizen science based biodiversity monitoring for birds, using an automated and easy-to-use multi-sensor feeder, can look like. 
A smart bird feeder including an environmental sensor, a microphone, as well as a balance and a camera in a wooden case which identifies the type of visiting birds using AI and publishes the recognized species, including all further collected data on an open access website. 
The station can be reproduced by anyone at an affordable price in a Do-It-Yourself format, making citizens a key contributor to biodiversity monitoring.

This repository contains the code to run the bird feeder which is equipped among other things with a camera, balance, microphone and further environmental sensors. 
All the collected data is sent to a server which is based on this [webserver](https://github.com/Birdiary/webserver). 
The repositories are currently still under development, the code for the operation of the feeder as well as for the web server are continuously updated. 
A corresponding manual for the operation of the system including open source instructions for building the feeder is available online: [Birdiary Manual](https://docs.google.com/document/d/1ItowLull5JF3irzGtbR-fCmgelG3B7DSaU1prOeQXA4/). 

Birdiary is a project which was launched by a group of students at the Institute for Geoinformatics at the University of Münster. 
If you got any questions contact us via: [info@wiediversistmeingarten.org](mailto:info@wiediversistmeingarten.org).

Any further information you can find via: [birdiary.de](https://www.wiediversistmeingarten.org/). 

## Advanced Software Development by the Community 
Citzien Scientists are driving the project substantially forward, leading to a large number of further developments. This also includes modifications to the code base. 
Some of these modifications are added directly here in the code (see [Suggest Feature](https://github.com/Birdiary/station?tab=readme-ov-file#suggest-feature)), but some are also hosted in separate repositories. 
In the following, we list these developments. We would like to inform you that no guarantee or liability is assumed for their functionality and ask you to contact the respective operators of the repositories directly if you have any questions.  

* [Birdiary Image Raspberry Pi Zero 2 W](https://osf.io/w8gef): The available PDF describes the necessary adjustments needed to enable the Birdiary image to be used on a Raspberry Pi Zero 2 W. 
* [betzBirdiary](https://github.com/herbbetz/betzBirdiary): Modified code base that may be of interest to those using the Raspberry Pi Zero 2 W or Raspberry Pi 4 Model B as microcontroller. The linked repository contains further modifications including a GUI. 
* [Birdiary on ESP32](https://github.com/tnier01/BirdiaryStationESP32/): The repository details how to run a Birdiary station using ESP32, especially Seeed Studio XIAO ESP32S3 Sense. 

## How to Contribute
Thank you for considering contributing to Birdiary. Birdiary is an open source project, and we love to receive contributions from our community — you!
There are many ways to contribute, from writing tutorials or blog posts, improving the design of the station, submitting bug reports and feature requests or writing code which can be incorporated into Birdiary itself.
We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.
This Repository comprises the code and issues for the station. Which means, if you want to contribute to the code running on the station, please contribute here. *Contributions in this repository do not have to stick to the code. They can also be about the hardware or design of the station.* Whereas when you want to contribute to the webserver (website), please use this repository [Webserver](https://github.com/Birdiary/webserver).

### Reporting Bugs
If you find a security vulnerability, do NOT open an issue. Email info@wiediversistmeingarten.org instead.
 
If you encounter a bug, check if the bug has already been reported as [issue](https://github.com/Birdiary/station/issues). If the bug has not been reported, you can open a [new issue](https://github.com/Birdiary/station/issues/new) to report the bug, please add the label "bug".
 
When filing an issue, make sure to answer these four questions:
> 1. Which hardware components (e.g. microcontroller, sensors) are you using?
> 2. Which software components (e.g. IDE, libraries, packages) are you using?
> 3. What did you do?
> 4. What did you expect to see?
> 5. What did you see instead?

### Suggest Feature
If you wish a special feature, feel free to add it as new [issue](https://github.com/Birdiary/station/issues/new). Here, please add the label "enhancement". We appreciate any suggestions.

### Code Contributions
Besides reporting bugs or suggesting features, we really appreciate code contributions. We suggest contributing through forking and pull-requests. A guideline how to fork a project and create a pull request can be found in the [Contribution to Projects Guidelines](https://docs.github.com/en/get-started/quickstart/contributing-to-projects). 
 
We review pull requests on a regular basis and give feedback or merge them directly into our main repository.

### Validating an Issue and Pull Requests
You can also contribute by merging a pull request into your local copy of the project and testing the changes. Add the outcome of your testing in a comment on the pull request.
Further, you can validate an issue or add additional context to an existing issue.
