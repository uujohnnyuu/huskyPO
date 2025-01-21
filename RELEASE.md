# huskium v1.0.2

## Overview
- **Enhancements** and **Bug Fixes** based on version 1.0.1.

## Enhancements
- **Type Hint**: Resolved mypy issues with `[return]` and `[return-value]`.

## Bug Fixes
- **Page**: Fixed missing return values in `supports_fedcm` and `dialog`.

## Installation
To install or upgrade to this version, run:
```sh
pip install huskium==1.0.2
```
---

# huskium v1.0.1

## Overview
- **New features**, **enhancements**, and **bug fixes** based on version 1.0.0.

## New Features
- **Elements**: Added methods to retrieve multiple elements' 
`get_dom_attributes`, `shadow_roots`, `aria_roles`, and `accessible_names` in a single operation.

## Enhancements
- **Elements**: Removed unnecessary methods like `all_visible_xxx` and `any_visible_xxx`, 
leaving users to extend them as needed.
- **Dynamic Element(s)**: Eliminated redundant validation 
when assigning dynamic elements with data descriptors.
- **Log**: Removed `logconfig` and merged its functionality into `logstack`.

## Bug Fixes
- **Error Message**: Fixed error messages in validation to correctly display the expected type name.

## Installation
To install or upgrade to this version, run:
```sh
pip install huskium==1.0.1
```
---

# huskium v1.0.0

## Overview
- Rename huskyPO to **huskium**.
- Update to Appium 4.4.0 (released on 2024/11/30).

## Installation
To install or upgrade to this version, run the following command:
```sh
pip install huskium==1.0.0
```