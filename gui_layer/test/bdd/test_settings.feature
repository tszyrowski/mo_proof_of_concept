Feature: Adjust application settings

  Scenario: Change contrast and font size in the settings
    Given the application is started
    When I open the settings menu
    And I adjust the contrast to 150
    Then the colors of the application should whiten
    When I adjust the font size to 20
    Then the font size across the application should increase

