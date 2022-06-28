# printestimate
This is a print estimating app that we plan to use in our own printing business. It follows the budgeted hourly rate type of costing, with features for including material costs, and custom cost add-ons in the estimates.

It is currently a work-in-progress.

**Tech Stack**
- Frontend : Vue 3, Tailwind css
- Backend : Django, Django Rest Framework, Postgresql

Bin packing algorithm used for paper imposition provided by [rectpack](https://github.com/secnot/rectpack).

A demo site can be viewed here: https://printestimate.herokuapp.com

**The backend "snoozes" when inactive. It might take a few seconds to wake up and retrieve records from the database.*
