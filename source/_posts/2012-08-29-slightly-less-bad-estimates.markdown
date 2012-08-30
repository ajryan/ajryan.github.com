---
layout: post
title: "Slightly Less Bad Estimates"
date: 2012-08-27 14:09
comments: true
categories: [development, estimation]
---

Estimation in software development is notoriously difficult, and very frequently incorrect. As estimates are reported up the chain, they are routinely "rounded up," and are still regularly exceeded. I have even tried to develop standard ratios to apply to each developer's estimates that wore sometimes accurate, but still were not always reliable (e.g. Bob usually estimates 50% of reality, Tom usually estimates 110% of reality). There is very often some unexpected factor that causes an estimate to be off.<!--more-->

## Effort != schedule

Another issue with reliability of estimates is that management often does not differentiate between effort estimates and schedule estimates. Consider the following scenario. You have one developer available and she just got started working on a task with a 40 hour estimate. A new task comes in and is assigned a 40 hour estimate. Management sees "40 hours == 1 week" and assumes the new task will be finished in a week, not considering the existing workload. A simple approach to dealing with this is to always include an estimated delivery date along with effort estimates. Keeping your task records updated with completed/remaining values and having a good reporting system that can project burndown helps too: just send your manager a link to the report.

## Checklist for slightly less bad estimates

Here are the factors I try to consider when providing an estimate:

* Research
* Proof-of-concept implementation
* Design documentation
* Management overhead
* History of "surprises" in the affected component
* Actual implementation
* Unit test development
* Build Engineering
* Test execution
  * Developer ad-hoc / exploratory
  * QA regression
  * QA actual testing
* Deployment

## Two-stage estimation

When possible, it can be reliable to split the a new user story across two sprints. Before the first sprint, estimate only the effort to research the scope of the change and do proof-of-concept work. The deliverables at the end of the first sprint are design documentation and an estimate of the actual development. This allows you to only estimate against known tasks, rather than try to predict potential surprises.
