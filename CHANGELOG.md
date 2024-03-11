# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# [1.9.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.8.1...v1.9.0) (2024-03-11)


### Bug Fixes

* **rovers:** use eval instead of ast.literal_eval ([39ce1b8](https://gitlab.laas.fr/rgodet1/tyr/commit/39ce1b8102153ff8b78b0ac29b0389d60f667339))


### Features

* **cli:** print starting time of resolution in bench verbose mode ([db83e41](https://gitlab.laas.fr/rgodet1/tyr/commit/db83e41b8d27e9cc0fb83caaaf4b1c7939e81a70))

## [1.8.1](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.8.0...v1.8.1) (2024-3-7)


### Bug Fixes

* **rovers:** add fix_dur version to fix upf issue ([1750e93](https://gitlab.laas.fr/rgodet1/tyr/commit/1750e93e919b1f4e5bdb990faff74b3c0c395266))
* **rovers:** add free_to_recharge task and methods ([15ba921](https://gitlab.laas.fr/rgodet1/tyr/commit/15ba92147f855e60db44f64a3b8ea22147b599e6))
* **rovers:** energy recharge rate calculation ([af0e82b](https://gitlab.laas.fr/rgodet1/tyr/commit/af0e82b70c99c41b91960791069d731ddeb991ad))

# [1.8.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.7.0...v1.8.0) (2024-2-9)


### Bug Fixes

* **tests:** cli bench ([2d0a75f](https://gitlab.laas.fr/rgodet1/tyr/commit/2d0a75fd7e0c4badc5eee4c2bc7c11df79c5792a))


### Features

* **cli:** command to solve one single problem ([f050f20](https://gitlab.laas.fr/rgodet1/tyr/commit/f050f20b4e08622aece57b7fc51dd90013a995d6))

# [1.7.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.6.2...v1.7.0) (2024-2-7)


### Bug Fixes

* **planner:** quality computation ([6012ed5](https://gitlab.laas.fr/rgodet1/tyr/commit/6012ed5f3767e569d8ef7c9b8ded3fbb21f340a9))
* **planner:** timeout on intermediate anytime result ([11f9c4e](https://gitlab.laas.fr/rgodet1/tyr/commit/11f9c4efc129a3fe78a2b4de13ce39bb1e8ea4c0))
* **problem:** convertion of goals into tasks ([71b132e](https://gitlab.laas.fr/rgodet1/tyr/commit/71b132ea12f3e47939067926b41296220827925e))
* **tests:** patch time.time for cli tests ([5e2212e](https://gitlab.laas.fr/rgodet1/tyr/commit/5e2212ead06e04d747b967f5c20a021a71dfefa1))
* **tests:** test_solve_get_version ([3cefbac](https://gitlab.laas.fr/rgodet1/tyr/commit/3cefbacc5b9f605c255f85062a60a63e883775e9))


### Features

* **database:** save and load planner results ([a16a74f](https://gitlab.laas.fr/rgodet1/tyr/commit/a16a74ff575a4eb049a2319560b90e2f931ecc54))
* **depots:** add reduce version ([469e286](https://gitlab.laas.fr/rgodet1/tyr/commit/469e2861435baf912b67d06e673c2c4216dd62ec))
* **domains:** add rcpsp ([a5245b1](https://gitlab.laas.fr/rgodet1/tyr/commit/a5245b1b2636279b261930e2786eadc0687c75d7))
* **domains:** add rovers ([30880f6](https://gitlab.laas.fr/rgodet1/tyr/commit/30880f6ea7efebbe9ac4eaf5bc289d067bcb9c4e))
* **domains:** add satellite ([fdea0d4](https://gitlab.laas.fr/rgodet1/tyr/commit/fdea0d459c0c9a2b6ca5950d7a0aeab598c76310))
* **domains:** getter for version names ([a11513e](https://gitlab.laas.fr/rgodet1/tyr/commit/a11513e558589bceab6cbaa37cb4ce10e58f07ec))
* **planners:** config for new domains ([a8bfc88](https://gitlab.laas.fr/rgodet1/tyr/commit/a8bfc8830de33c272482ebf85b3b6d1d8910922f))

## [1.6.2](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.6.1...v1.6.2) (2024-1-23)


### Bug Fixes

* **cli:** shared variable through processes ([ab3163c](https://gitlab.laas.fr/rgodet1/tyr/commit/ab3163c5b1e0ed14eeb2bf85811c0d9e09f45eb1))

## [1.6.1](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.6.0...v1.6.1) (2024-1-23)


### Bug Fixes

* **cli:** parallelization ([497e528](https://gitlab.laas.fr/rgodet1/tyr/commit/497e52864fd1f7fd69c14379464025b762f6fce9))

# [1.6.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.5.0...v1.6.0) (2024-1-23)


### Bug Fixes

* **bench termimal writter:** right fill short summary items ([3b1472f](https://gitlab.laas.fr/rgodet1/tyr/commit/3b1472fb5956a5accb5478dc43b66d7ffb0fbdd6))
* **planner:** anytime behavior ([fa86f57](https://gitlab.laas.fr/rgodet1/tyr/commit/fa86f576be45389edb42d542546a5627bb58a28a))
* **planner:** reset last result ([7fb9a6a](https://gitlab.laas.fr/rgodet1/tyr/commit/7fb9a6a65b6b02a44f8b4225ed1c6ca55722c31d))
* **tests:** disable crop timeout feature ([e78df6b](https://gitlab.laas.fr/rgodet1/tyr/commit/e78df6bce965227498ecfbffd7da74f4426761b5))
* **tests:** make bench cli tests machine independent ([5905317](https://gitlab.laas.fr/rgodet1/tyr/commit/59053173a028c12db71a5c64c383361d6c340542))


### Features

* **bench:** handle multiple jobs ([51f851d](https://gitlab.laas.fr/rgodet1/tyr/commit/51f851d926e62a38e04f17a80ed3fe1c35e48d22))
* **cli:** add basic benchmark ([17edd9b](https://gitlab.laas.fr/rgodet1/tyr/commit/17edd9b36e3420b0cd8a947369a31272da451032))
* **cli:** add filters on planners and problems ([6de24e3](https://gitlab.laas.fr/rgodet1/tyr/commit/6de24e3d8e0aaefb569ad13e42ec8fa2d15459a0))
* **cli:** can specify multiple outputs ([a678a7b](https://gitlab.laas.fr/rgodet1/tyr/commit/a678a7b9cf1a0a18965da401e927a86cccde755e))
* **planner config:** add oneshot/anytime names ([54c6ff0](https://gitlab.laas.fr/rgodet1/tyr/commit/54c6ff093f120dc418ce6ca411ce293df5a97a86))
* **planner:** disable credit stream ([cf619aa](https://gitlab.laas.fr/rgodet1/tyr/commit/cf619aa7cfad710da0033b325fefe6226b34a918))
* **planners:** add lpg ([06d6f9e](https://gitlab.laas.fr/rgodet1/tyr/commit/06d6f9ea3bc5624868455ca6d2d72f80c0c2b59e))
* **planners:** support anytime ([082a744](https://gitlab.laas.fr/rgodet1/tyr/commit/082a744da919037afea6e6db994a6a69c699ebb1))


### Reverts

* **tests:** planner solving ([706bf14](https://gitlab.laas.fr/rgodet1/tyr/commit/706bf147a3a687aa027de0fefae10a6efe65bdcd))

# [1.5.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.4.1...v1.5.0) (2024-1-19)


### Bug Fixes

* **ci:** make docker needs optional ([4214f6f](https://gitlab.laas.fr/rgodet1/tyr/commit/4214f6fc78ef4e1cb4395e35b235499d42d91434))
* **ci:** use node:latest for commitlint ([181ad4e](https://gitlab.laas.fr/rgodet1/tyr/commit/181ad4e8b737b16a0f41146d663c2e652e6de42d))
* **ci:** use node:latest for release ([52a7a85](https://gitlab.laas.fr/rgodet1/tyr/commit/52a7a85746fd707ac760bd7c69661ee4972896f2))
* **planner result:** convertion of upf plan into string ([335e4df](https://gitlab.laas.fr/rgodet1/tyr/commit/335e4dfd858810b8a524fac3ca03214e516de812))
* **tests:** register planners before solving problems ([4c04e42](https://gitlab.laas.fr/rgodet1/tyr/commit/4c04e422aec44efeb36feabdb665ffc72c2a4746))
* **typing:** list and optional for python3.8 ([c7c3f58](https://gitlab.laas.fr/rgodet1/tyr/commit/c7c3f58fb0c46299d37734a842f3f34c42ac7dbd))
* **up:** register planners manually ([3383e9c](https://gitlab.laas.fr/rgodet1/tyr/commit/3383e9ca964f41707cc1acc37ae0010a68c63a9a))


### Features

* **core:** add log and root directories constants ([3c793cb](https://gitlab.laas.fr/rgodet1/tyr/commit/3c793cbf822bfbd7b470c2343a45f993872eb5d8))
* **domain:** getter of number of instances ([cf947d8](https://gitlab.laas.fr/rgodet1/tyr/commit/cf947d85b5a8f164dec1c5b8334d38302fe91599))
* **pddl planner:** override _solve to get plan from process output if needed ([ee4f5ca](https://gitlab.laas.fr/rgodet1/tyr/commit/ee4f5ca23eea417aabed55628a320a663bb92c82))
* **planner config:** add config dataclass for resolution ([14d1035](https://gitlab.laas.fr/rgodet1/tyr/commit/14d1035ec326ed94e29614c6f157e12a5a226fc1))
* **planner config:** add hash ([7d15edf](https://gitlab.laas.fr/rgodet1/tyr/commit/7d15edfa6a9d09fe6a2bb402a91aad06f5fc5ceb))
* **planner config:** can specify env variables to set ([da4023c](https://gitlab.laas.fr/rgodet1/tyr/commit/da4023c2c34b6a6d7c6c0925a34b45f280852b7c))
* **planner result:** factory for error ([3ab74c9](https://gitlab.laas.fr/rgodet1/tyr/commit/3ab74c9fac8661ee5e2f7c4efc3fd44be445ff03))
* **planner result:** factory for timeout ([6b5bc44](https://gitlab.laas.fr/rgodet1/tyr/commit/6b5bc44c137b482c49270f622f61cdb2f4d41e42))
* **planner result:** factory for unsupported ([906c1e3](https://gitlab.laas.fr/rgodet1/tyr/commit/906c1e39001f3f0d6ae20bf3987aa6081c4b64f8))
* **planner scanner:** get all planners ([9ee6510](https://gitlab.laas.fr/rgodet1/tyr/commit/9ee6510af5f9a6ec1d907b4bb9a0b57b9aa4cfbc))
* **planner:** abstract version for PDDL planners ([1600b82](https://gitlab.laas.fr/rgodet1/tyr/commit/1600b82444e0842eab6002d6516d83bb4023f888))
* **planner:** add hash and eq ([9b4a37b](https://gitlab.laas.fr/rgodet1/tyr/commit/9b4a37b64f9f8955a4ecc8974b3533386994847c))
* **planner:** add Planner ([03a6374](https://gitlab.laas.fr/rgodet1/tyr/commit/03a63745c646202892940dcf22eed99ff6f822bc))
* **planner:** add planner config scanner ([afeae4e](https://gitlab.laas.fr/rgodet1/tyr/commit/afeae4e6e097b996ceb7c43e7584f57489a3b61c))
* **planner:** add PlannerConfig ([58bebcb](https://gitlab.laas.fr/rgodet1/tyr/commit/58bebcb05e1c8307ad689fa62010ac24900e656a))
* **planner:** add PlannerResult ([9859efb](https://gitlab.laas.fr/rgodet1/tyr/commit/9859efb2e42ed37951bc3e8897d3adf63015e7d9))
* **planner:** can specify the name of the log file ([f65f256](https://gitlab.laas.fr/rgodet1/tyr/commit/f65f2565a5d4eb9aaf334dabc55fa89770940258))
* **planner:** clear the logs before solving ([f28d3fd](https://gitlab.laas.fr/rgodet1/tyr/commit/f28d3fd1c15dc8fe53590f51537ee05bec404048))
* **planners:** add Aries config ([39662b5](https://gitlab.laas.fr/rgodet1/tyr/commit/39662b5221dac16cf6b98fbb318990212e823bce))
* **planners:** add Optic ([1e28108](https://gitlab.laas.fr/rgodet1/tyr/commit/1e281081cd42b715dcaf4dca4b51fbc6b0e7d296))
* **planner:** save errors in logs ([34891e6](https://gitlab.laas.fr/rgodet1/tyr/commit/34891e64c7e27e2578567db87a162181e72c463c))
* **planner:** set env variables before solving ([8f2e906](https://gitlab.laas.fr/rgodet1/tyr/commit/8f2e906a20fdbfcb0a1fd38c5eb6103c9e13a0c4))
* **planner:** skip compatibility checks ([27a480d](https://gitlab.laas.fr/rgodet1/tyr/commit/27a480d4b29bd9d2b48169b4b47009032eb7b272))
* **problems:** add jobshop scheduling and temporal numeric ([9a9dadb](https://gitlab.laas.fr/rgodet1/tyr/commit/9a9dadbde645cb0d8072c0256b545dc5252333cf))
* **problems:** can extracte the quality of a plan ([754b1de](https://gitlab.laas.fr/rgodet1/tyr/commit/754b1de121049c567c61e02e86684cf8bf19fb3d))


### Reverts

* **docker:** remove PYTHONPATH ([f64bd1d](https://gitlab.laas.fr/rgodet1/tyr/commit/f64bd1dd552e51fde3a2e8ed37d4ba2518fd5125))

## [1.4.1](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.4.0...v1.4.1) (2024-1-15)

# [1.4.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.3.0...v1.4.0) (2024-1-14)


### Bug Fixes

* **converter:** make a copy of goals ([dc48794](https://gitlab.laas.fr/rgodet1/tyr/commit/dc4879458db781cfea0a71a7b0d130dee7a10fca))


### Features

* **domains/depots:** add hierarchical numeric base version ([931cf17](https://gitlab.laas.fr/rgodet1/tyr/commit/931cf17a6d1448e056cdc7094fbee206f7f1d6d4))
* **domains/depots:** add hierarchical temporal numeric base and no div versions ([8a90772](https://gitlab.laas.fr/rgodet1/tyr/commit/8a90772218b4ab7519a62115129958d3dfa69599))
* **domains/depots:** add no-div version to temporal-numeric ([f394094](https://gitlab.laas.fr/rgodet1/tyr/commit/f39409422be93827447c9a5b22c9ca05854bd8b0))
* **domains/depots:** add numeric base version ([63172cd](https://gitlab.laas.fr/rgodet1/tyr/commit/63172cdb8ebcf0b67db21cb520eaebc5a0e5b199))
* **problem:** add converter from goals to tasks ([1efa194](https://gitlab.laas.fr/rgodet1/tyr/commit/1efa194d2ffe95ad189ee1acfcfc1647d7f9fdb9))

# [1.3.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.2.1...v1.3.0) (2024-1-12)


### Features

* **domains/depots:** add hierarchical and temporal-numeric variants with base versions ([066aa77](https://gitlab.laas.fr/rgodet1/tyr/commit/066aa7753c260cd96d542cff24450c828fd1e793))

## [1.2.1](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.2.0...v1.2.1) (2024-1-12)


### Reverts

* **problem:** remove variant layer ([fd1e26e](https://gitlab.laas.fr/rgodet1/tyr/commit/fd1e26e40548d8eef23f6d89c38840ec01418f61))

# [1.2.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.1.2...v1.2.0) (2024-1-12)


### Features

* **problem:** util function to get all domains from module ([8a6b4ea](https://gitlab.laas.fr/rgodet1/tyr/commit/8a6b4eadeebdd2b52703392927c7f24f2cdab5fc))

## [1.1.2](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.1.1...v1.1.2) (2024-1-12)


### Bug Fixes

* **ci:** exists rule ([7f6f241](https://gitlab.laas.fr/rgodet1/tyr/commit/7f6f24102777022b66416267ed570579d5c24da7))
* **ci:** pip install local code ([e845ca9](https://gitlab.laas.fr/rgodet1/tyr/commit/e845ca9b96199b8761d0c8d1940787e69a26ebd1))
* **ci:** remove python3.9 and python3.10 ([8a5f6c7](https://gitlab.laas.fr/rgodet1/tyr/commit/8a5f6c7e513a49fcc5a917b865802a22c5e02ecf))
* **tests:** remove autospec ([0f04286](https://gitlab.laas.fr/rgodet1/tyr/commit/0f042867f3fefc18fa3a6b1072e8b104dbc44bbc))


### Reverts

* remove autospec from tests ([e0e1737](https://gitlab.laas.fr/rgodet1/tyr/commit/e0e1737d046bebfdd99abe4217ad7ef2531156ed))

## [1.1.1](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.1.0...v1.1.1) (2024-1-12)

# [1.1.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.0.1...v1.1.0) (2024-1-12)


### Features

* **patterns:** add Abstract ([978f24c](https://gitlab.laas.fr/rgodet1/tyr/commit/978f24cca91785382b693816119911743cfb91a6))
* **patterns:** add AbstractSingleton metaclass ([d495f6b](https://gitlab.laas.fr/rgodet1/tyr/commit/d495f6b1ec0874a369af0832c8e2528ae354ee32))
* **patterns:** add Lazy ([5f4e421](https://gitlab.laas.fr/rgodet1/tyr/commit/5f4e421ddae979c96894b15637f69b662d4ce5ac))
* **patterns:** add Singleton ([6e76c06](https://gitlab.laas.fr/rgodet1/tyr/commit/6e76c06d5afb0e283f94602c37a5726ad588ef91))
* **problem:** add domain creation logic and models ([ec61e4c](https://gitlab.laas.fr/rgodet1/tyr/commit/ec61e4c637b5a2c5d59f6de2a5747e8a01bb0ddb))

## [1.0.1](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.0.0...v1.0.1) (2024-1-4)


### Bug Fixes

* not skip ci on version bump ([15947f0](https://gitlab.laas.fr/rgodet1/tyr/commit/15947f0489e5ea0fc866e9c932205716a3362a85))

# 1.0.0 (2024-1-4)


### Features

* **ci:** initialization ([36338ae](https://gitlab.laas.fr/rgodet1/tyr/commit/36338ae5188dfc6b6c0a67a1a569b052af3541b4))
