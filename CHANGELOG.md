# 📝 Changelog

All notable changes to Terra Scout will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added

- Initial project structure (Phase 0)
- Documentation framework
- Architecture decision records
- Setup and troubleshooting guides
- Mineflayer bot with mining patterns (Phase 1)
- Python-Node.js bridge layer (Phase 1)
- Custom Gymnasium environment (Phase 2)
- PPO training pipeline with Stable-Baselines3 (Phase 2)
- Custom reward calculator with survival awareness
- 20-action discrete action space for mining
- Metrics tracking and JSON export

### Changed

- Migrated from MineRL to Mineflayer + Bridge architecture (ADR-002)
- Updated documentation to reflect new architecture

### Fixed

- JSON serialization bug with numpy float32 in metrics.py

### Security

- N/A

---

## [0.1.0] - 2025-XX-XX (Planned)

### Added

- MineRL environment integration
- Basic PPO agent implementation
- Training pipeline
- Evaluation scripts

---

## Version History

| Version | Date       | Description                  |
| ------- | ---------- | ---------------------------- |
| 0.1.0   | TBD        | Initial agent implementation |
| 0.0.1   | 2025-XX-XX | Project structure            |

---

## Versioning

Terra Scout uses [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)
