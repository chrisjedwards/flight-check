# Phase 4: Problems and Solutions

| Phase          | Problem                                                        | Solution                                                            |
| -------------- | -------------------------------------------------------------- | ------------------------------------------------------------------- |
| Research       | No access to source code, only a video                         | Watched the recording step by step and documented what I saw        |
| Research       | Original API key visible in the video                          | Use my own key in `.env`, never reproduce the original              |
| Research       | Unclear assignment scope                                       | Clarified with supervisor and teacher, split work into six steps    |
| Research       | API returned 400 Bad Request with a valid key                  | Added the required `Accept: application/json` header                |
| Research       | D/I guess based only on a label in the video                   | Verified against real data, found three values (D, S, I)            |
| Research       | Original app shows +1 hour offset (CET)                        | Use `ZoneInfo("Europe/Stockholm")` to handle summer and winter time |
| Implementation | Virtual environment created in a different folder than planned | Verified `.gitignore`, kept the location                            |
| Implementation | Port 8000 already in use                                       | Found and stopped the process with `lsof` and `kill`                |
| Implementation | Outdated Xcode blocked Homebrew                                | Updated Xcode, reinstalled the package                              |
| Implementation | Risk of committing secrets                                     | Verified with `git check-ignore` before the first commit            |
| Implementation | Static mount on `/` can catch API routes                       | Defined API routes before the mount                                 |
| Implementation | Tests calling the real API would use the quota                 | Used a saved real API response as test data                         |
| Implementation | Unsure about departure field names                             | Verified with one live API call                                     |
| Implementation | Risk of using up the 10,000 request limit                      | Added a 60-second in-memory cache                                   |
| Implementation | Deprecation warning in pytest                                  | Confirmed it comes from libraries, not my code                      |
| Implementation | City name matching failed for names like "London LHR"          | Mapped countries by IATA code with OurAirports data                 |
| Implementation | Airport dataset too large (9,054 airports)                     | Filtered on scheduled service, reduced to 4,155                     |
| Implementation | Filtering could remove real destinations                       | Coverage-check script and tests, 100% verified                      |
| Implementation | Duplicate IATA codes in the dataset                            | Preferred large, then medium, then small airports                   |
| Implementation | Unknown IATA codes or missing data file                        | Fallback and one-time warning instead of crash                      |
