# Changelog - mdIngest (`md-publish`)

All notable changes to the **mdIngest** open-source Rust ingestion and publishing binary CLI tool will be documented in this file.

The project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and follows a **weekly release update strategy** toward a stable `v1.0.0` core engine.

---

## [0.1.0] - 2026-08-01

### 🚀 Initial Open-Source Alpha Release (`v0.1.0`)

* **Rust CLI Engine (`md-publish`):** Standalone zero-dependency compiled binary built with Rust (`crate/src/`) for deterministic markdown ingestion, Google Docs export sanitization, and KaTeX math expression hardening.
* **Deterministic Substrate:** Platform-agnostic preprocessor executable (`coolchain`/`md-publish`) operating on `mdBook` structures across Windows, macOS, and Linux.
* **Mempool & Template Staging (`--park` / `--unpark`):** Built-in CLI commands for triaging unconfirmed drafts (`src/_slug.md`) and promoting reviewed research papers to numeric episode keys (`src/245.md`).
* **Zero Asset Coupling:** Completely decoupled from episode media payloads and text ledgers (which reside in the `deepDive` kitchen repository).

---

## 📅 Release Management & Product Roadmap

```
  v0.1.0 (Current) ➔ v0.2.0 (Weekly Hardening) ➔ ... ➔ v1.0.0 (Stable Engine) ➔ Desktop / Mobile Wrappers
```

* **v0.1.0 (Current Alpha):** Initial open-source Rust binary CLI release for mdBook sanitization and indexer logic.
* **v0.2.0 - v0.9.0 (Weekly Updates):** Weekly upstream bugfix iterations, performance hardening, enhanced KaTeX error bounds, and schema validation.
* **v1.0.0 (Stable Core):** Enterprise-grade deterministic publishing engine.
* **Future Phase (v2.0+):** Native cross-platform desktop UI wrappers (Windows / macOS) and mobile build tooling (iOS / Android).
