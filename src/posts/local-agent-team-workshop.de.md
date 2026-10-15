---
title: Ein Quellenprüfer scheiterte an Markdown-Kontexten
date: '2026-10-15'
lang: de
translationKey: local-agent-team-workshop
slug: markdown-quellenpruefung-und-review
tags:
  - Markdown
  - Softwareentwicklung
  - Qualitätssicherung
excerpt: >-
  Ein lokaler Test deckte vier falsche Freigaben in einem Quellenlink-Prüfer
  auf. Die Gegenprüfung änderte die Entscheidung: kein Einsatz des Kandidaten.
draft: true
---

Ein kleiner Prüfer sollte sicherstellen, dass ein deutscher und englischer Blogentwurf jeweils einen Quellenlink enthalten. Seine eigenen Tests liefen durch. Eine unabhängige Gegenprüfung fand trotzdem vier Fälle, in denen er ein Dokument ohne echten Quellenlink akzeptierte.

Der Prüfer suchte nach Linkmustern im Text. Das reicht nicht: Markdown unterscheidet zwischen Links, Bildern, Codeblöcken und HTML. Die [CommonMark-Spezifikation](https://spec.commonmark.org/0.31.2/) beschreibt diese Formen getrennt. Ein Linkmuster innerhalb eines Codebeispiels oder HTML-Kommentars belegt keine Quelle im Artikel.

## Der konkrete Fehlversuch

Bei einer erneuten lokalen Prüfung am 15. Oktober 2026 lief die Testsuite des Kandidaten mit neun Tests durch. Die unabhängige Gegenprüfung erwartete zusätzlich, dass der Prüfer ablehnt, wenn der einzige scheinbare Link in einem Tilde-Codeblock, eingerücktem Code, einem HTML-Kommentar oder einer Bildsyntax steht. In allen vier Fällen gab der Prüfer stattdessen Erfolg zurück.

Diese Ergebnisse lassen sich in der lokalen Prüfarbeitskopie reproduzieren. Sie belegen einen eng umrissenen Fehler dieser Kandidatenversion; sie sagen nichts über Markdown-Prüfer allgemein aus. Der Kandidat wurde daraufhin nicht übernommen. Die Ablehnung zeigt keine erfolgreiche Selbstverbesserung. Sie zeigt, dass ein bestandener eigener Testlauf für die Übernahme nicht genügte.

## Was diese Beobachtung trägt

Ein automatisierter Check kann das falsche Kriterium erfüllen und dennoch grün melden. Bei diesem Beispiel war die Frage nicht, ob irgendwo ein Linkmuster vorkam, sondern ob ein wirklicher Quellenlink im Artikeltext stand. Die externe Spezifikation half, die Syntax auseinanderzuhalten; erst die lokalen Gegenbeispiele belegten das Verhalten des Prüfkandidaten.

Der Befund ist klein und lokal. Er belegt weder, dass die Ablehnung fachlich in jeder Hinsicht richtig war, noch dass weitere Prüfschritte zuverlässig sind. Er belegt auch keine bessere Produktivität oder allgemeine Qualität des Agententeams. Sichtbar ist nur eine sinnvolle Grenze: Ein Vorschlag kann geprüft und zurückgewiesen werden, bevor er Teil des verwendeten Werkzeugbestands wird.

Dieser Beitrag entstand mit Unterstützung von KI. Die geschilderten Testresultate wurden am 15. Oktober 2026 lokal erneut ausgeführt; die Veröffentlichung dieser Beobachtung macht sie nicht zu einem allgemeinen Qualitätsnachweis.
