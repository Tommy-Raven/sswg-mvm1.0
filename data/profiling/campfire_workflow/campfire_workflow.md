# Workflow campfire_workflow

**Workflow ID:** `campfire_workflow`

## Phases
### Preparation
### Construction
### Ignition & Management
### Extinguish & Leave No Trace

## Modules
- {'module_id': 'm01_location_check', 'phase_id': 'phase_1', 'name': 'Location & Permits', 'inputs': [], 'outputs': ['site_approved'], 'dependencies': [], 'ai_logic': 'Check local regulations, assess proximity to vegetation, evaluate wind conditions.', 'human_actionable': 'Inspect site. If no local ban and a 10 ft cleared area exists, mark site_approved = true.'}
- {'module_id': 'm02_materials_gather', 'phase_id': 'phase_1', 'name': 'Gather materials', 'inputs': [], 'outputs': ['tinder_set', 'kindling_set', 'fuelwood_set'], 'dependencies': ['m01_location_check'], 'ai_logic': 'List locally available tinder, kindling, and fuelwood types and quantities.', 'human_actionable': 'Collect dry tinder (leaves, birch bark), kindling (small sticks), and fuel wood (split logs).'}
- {'module_id': 'm03_build_structure', 'phase_id': 'phase_2', 'name': 'Build fire structure', 'inputs': ['tinder_set', 'kindling_set'], 'outputs': ['structure_ready'], 'dependencies': ['m02_materials_gather'], 'ai_logic': 'Recommend a structure (teepee, log cabin) based on available materials.', 'human_actionable': 'Construct a small teepee of kindling over tinder, leaving airflow paths.'}
- {'module_id': 'm04_ignite', 'phase_id': 'phase_3', 'name': 'Ignition', 'inputs': ['structure_ready'], 'outputs': ['fire_lit'], 'dependencies': ['m03_build_structure'], 'ai_logic': 'Provide step sequence for safe ignition (sparks, matches, lighter), monitor smoldering risk.', 'human_actionable': 'Ignite tinder carefully; feed small kindling until sustained flame.'}
- {'module_id': 'm05_manage', 'phase_id': 'phase_3', 'name': 'Manage burn', 'inputs': ['fire_lit'], 'outputs': ['burn_controlled'], 'dependencies': ['m04_ignite'], 'ai_logic': 'Advise on safe adding of fuel wood, monitor wind changes, advise extinguishing if unsafe.', 'human_actionable': 'Add fuel wood gradually, maintain a small, controlled flame.'}
- {'module_id': 'm06_extinguish', 'phase_id': 'phase_4', 'name': 'Extinguish', 'inputs': ['burn_controlled'], 'outputs': ['site_clean'], 'dependencies': ['m05_manage'], 'ai_logic': 'Provide steps to fully extinguish (soak, stir, feel for heat) and restore site.', 'human_actionable': 'Douse with water, stir ashes, ensure cold-to-touch, scatter cooled rocks, fill any holes.'}

## Evaluation
- **clarity**: None
- **coverage**: None
- **feasibility**: None
- **alignment**: None
- **notes**: []
- **quality**: {'overall_score': 0.5387210884353741, 'metrics': {'clarity': 0.65, 'coverage': 1.0, 'coherence': 1.0, 'completeness': 0.0, 'intent_alignment': 1.0, 'specificity': 0.12104761904761906, 'usability': 0.0}}
- **meta_metrics**: {'timestamp': '2025-12-27T09:09:12.495308+00:00', 'scores': {'clarity': 0.65, 'coverage': 1.0, 'coherence': 1.0, 'completeness': 0.0, 'intent_alignment': 1.0, 'specificity': 0.12104761904761906, 'usability': 0.0}, 'overall_score': 0.5387210884353741, 'baseline': {'status': 'missing', 'overall_score': None, 'scores': None}, 'deltas': {'overall_score': None, 'metrics': {}}, 'thresholds': {'promotion_threshold': 0.02, 'regression_guard': -0.05, 'guard_metrics': ['clarity', 'coherence', 'completeness', 'intent_alignment', 'usability']}, 'decision': {'promotion_eligible': False, 'regression_guard_passed': True}, 'evidence_notes': ['Core metrics computed on the current workflow snapshot.', 'Baseline compared against latest stored workflow version.']}