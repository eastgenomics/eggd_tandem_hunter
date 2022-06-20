# GitLab Description Templates
## Overview
This repository contains generic description templates for use in GitLab.

They are intended to be used to harmonise the Git workflow used by YNE GLH
Central bioinformaticians across projects.

At present templates are available for the following:
  * Issue templates
    * Bug
    * Feature request
  * Merge request templates
    * Bug
    * Feature
    * Production release

## Usage
To use these templates:
  1. Clone this repository into the top level of the git repository (repo) of
  your project.

  ```bash
  git clone https://gitlab.com/leedsgeneticslaboratory/gitlab_templates.git .gitlab
  ```

  2. Remove the `.git` directory within  the `.gitlab` directory to play nicely
  with your project's git repo.

  ```bash
  rm -r .gitlab/.git
  ```

  3. Track and commit the `.gitlab` description templates directory in your git
  repo.

  ```bash
  git add .gitlab
  git commit -m "GitLab description templates added"
  ```

Once cloned and added to your own repo the templates can be customised to meet
the needs of your project.

**Note:** At present if you add the above repo as a submodule named `.gitlab` to
your project repo the GitLab web interface does not recognise the templates
within it. This means they are not available to use, hence the usage suggested
above.
