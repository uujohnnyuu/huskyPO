# Release Note for v1.2.0

## Overview
This release focuses on improvements of logstack.

## Improvements
- **logstack**: Significantly enhanced the performance of searching for a specified module or function frame.

## Installation or Upgrade Instructions
To install or upgrade to this version, run the following command:
```sh
pip install huskypo==1.2.0
```


# Release Note for v1.1.2

## Overview
This release focuses on bug fixes and stability improvements.

## Bug Fixes
- **element**: Fixed an issue where the select object’s temporary information was not deleted after the page instance was changed.

## Installation or Upgrade Instructions
To install or upgrade to this version, run the following command:
```sh
pip install huskypo==1.1.2
```


# Release Note for v1.1.0

## Overview
This release includes significant new features, improvements, bug fixes and deprecations.

## New Features
- **config**: Added `offset` and `area` for `swipe` and `flick` relative functions.
- **page**: Added commonly used methods for Selenium 4.0 and Appium 2.0.
- **element**: Added commonly used methods for Selenium 4.0 and Appium 2.0.
- **elements**: Added methods related to visibility status.
- **ec_extension**: Refactored all existing methods and exception handling for more flexible WebDriverWait operations.

## Improvements
- **page**: Optimized data flow and property control, improving performance and stability.
- **element**: Optimized data flow and property control, improving performance and stability.
- **logstack**: Enhanced the performance of searching for specified function frames.

## Bug Fixes
- **decorator**: Fixed the issue where the function name was always `wrapper` when calling the dynamic element `__name__` attribute.
- **element**: Fixed the issue where the `remark` attribute could not be dynamically updated.
- **elements**: Fixed the issue where the `remark` attribute could not be dynamically updated.

## Deprecations
- **by**: `SwipeAction` has been replaced by `Offset` and `Area` in the `config`.
- **page**: `swipe_ratio` has been replaced by `swipe_by` and `flick_by`.
- **element**: `wait_not_xxx` methods have been renamed to xxx's antonyms; `swipe_into_view` has been replaced by `swipe_by` and `flick_by`.
- **elements**: `wait_not_xxx` methods have been renamed to xxx's antonyms.

## Installation or Upgrade Instructions
To install or upgrade to this version, run the following command:
```sh
pip install huskypo==1.1.0
```