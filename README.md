# BDD Tag Expression Processor

The module wil filter the Feature files based on the given scenario tag expressions. The expression can be created
freehand in the following format.

## Rules

* All the Feature files must have at least a single line space between each block in the feature files.
  * _Feature, Background, Scenario, Scenario Outline_
* The Left side is always the ANDs and Right side is always the ORs
* The bridge between ANDs and ORs is **and (**
* Tags that we want to exclude are prefixed with a ~ symbol.
    * _Eg. NoRuns can be either the default ~@norun or any tags such as ~@p3_
* All the scenarios that are filtered are arranged back into their original files and a @final tag is placed in the tag
  list
  * _All the comments, and extra spaces are removed from the feature file_

## Test Samples

```
Given expression: {@web}
	 Result: --> NoRuns: [],  Ands: ['@web'], Ors: []

Given expression:   {  @web    and @regression    and ~@norun}
	 Result: --> NoRuns: ['@norun'],  Ands: ['@web', '@regression'], Ors: []

Given expression: {~@norun and @web and (@test1 or @test2)}
	 Result: --> NoRuns: ['@norun'],  Ands: ['@web'], Ors: ['@test1', '@test2']

Given expression: {~@norun and (@test1 or @test2)}
	 Result: --> NoRuns: ['@norun'],  Ands: [], Ors: ['@test1', '@test2']

Given expression: {@web and ~@browser and @sanity and ~@norun}
	 Result: --> NoRuns: ['@browser', '@norun'],  Ands: ['@web', '@sanity'], Ors: []

Given expression: {~@norun}
	 Result: --> NoRuns: ['@norun'],  Ands: [], Ors: []

Given expression: {@sanity or @regression}
	 Result: --> NoRuns: [],  Ands: [], Ors: ['@sanity', '@regression']

Given expression: {@web and @browser and ~@norun and (@regression or @Sanity)}
	 Result: --> NoRuns: ['@norun'],  Ands: ['@web', '@browser'], Ors: ['@regression', '@Sanity']

Given expression: {@web and ~@norun and (@regression or @Sanity)}
	 Result: --> NoRuns: ['@norun'],  Ands: ['@web'], Ors: ['@regression', '@Sanity']

Given expression: {  ~@web   and   @browser   and   @checkout   and    ~@norun and (  @regression   or   @Sanity    )}
	 Result: --> NoRuns: ['@web', '@norun'],  Ands: ['@browser', '@checkout'], Ors: ['@regression', '@Sanity']

Given expression: {  ~@web   and   @browser   and   @checkout   and    @norun and (  @test1   or   @test2    )}
	 Result: --> NoRuns: ['@web'],  Ands: ['@browser', '@checkout', '@norun'], Ors: ['@test1', '@test2']

Given expression: {  @web   and   @regression   and    @norun and (  @test1   or   @test2    )}
	 Result: --> NoRuns: [],  Ands: ['@web', '@regression', '@norun'], Ors: ['@test1', '@test2']

Given expression: {@web and (@regression or @Sanity)}
	 Result: --> NoRuns: [],  Ands: ['@web'], Ors: ['@regression', '@Sanity']

Given expression: {  @web   and   ~@browser   and   ~@checkout   and    @norun and (  @regression   or   @Sanity    )}
	 Result: --> NoRuns: ['@browser', '@checkout'],  Ands: ['@web', '@norun'], Ors: ['@regression', '@Sanity']

Given expression: {@web and ~@norun and (@p1)}
	 Result: --> NoRuns: ['@norun'],  Ands: ['@web'], Ors: ['@p1']

Given expression: @web
	 Result: --> NoRuns: [],  Ands: ['@web'], Ors: []

Given expression: 
	 Result: --> NoRuns: [],  Ands: [], Ors: []

Given expression: {~@test-2}
	 Result: --> NoRuns: ['@test-2'],  Ands: [], Ors: []

Given expression: {~@norun and @web}
	 Result: --> NoRuns: ['@norun'],  Ands: ['@web'], Ors: []
```
