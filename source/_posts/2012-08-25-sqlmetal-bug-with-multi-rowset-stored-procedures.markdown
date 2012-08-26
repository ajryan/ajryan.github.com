---
layout: post
title: "SqlMetal bug with multi-rowset stored procedures"
date: 2012-08-25 15:54
comments: true
categories: [development, sql, linq-to-sql, bugs]
---

The Issue
----

When a stored procedure has multiple result sets with the same type signature, only the first rowset with the given signature is included in the generated DBML.

Resolution
----

A simple fix is to swap the position of columns in one of the rowsets.

Connect
----

I have posted this issue to Microsoft Connect. If it affects you, please visit and vote.