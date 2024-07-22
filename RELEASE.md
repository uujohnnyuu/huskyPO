# Release Note for v1.1.0

## Overview
This release includes significant new features, bug fixes, and performance improvements.

## New Features
- **config**: Added offset and area for swipe and flick relative functions.
- **page**: Added commonly used methods for Selenium 4.0 and Appium 2.0.
- **element**: Added commonly used methods for Selenium 4.0 and Appium 2.0.
- **elements**: Added methods related to visibility status.
- **ec_extension**: Refactored all existing methods and exception handling for more flexible WebDriverWait operations.

## Bug Fixes
- **decorator**: Fixed the method of dynamically retrieving attribute information (@wraps).

## Improvements
- **page**: Optimized data flow and property control, improving performance and stability.
- **element**: Optimized data flow and property control, improving performance and stability.
- **logstack**: Enhanced the performance of searching for specified function frames.

## Installation or Upgrade Instructions
To install or upgrade to this version, run the following command:
```sh
pip install huskypo==1.1.0