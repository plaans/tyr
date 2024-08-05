# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.20.1](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.20.0...v1.20.1) (2024-08-05)


### Bug Fixes

* **just:** update popcorn submodule during install ([7d6bf58](https://gitlab.laas.fr/rgodet1/tyr/commit/7d6bf58308f8138b45cf47309b1728045cf754e6))

# [1.20.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.19.8...v1.20.0) (2024-08-05)


### Features

* **table:** can auto bold best and worst result per row ([fcd5896](https://gitlab.laas.fr/rgodet1/tyr/commit/fcd5896a16b6ef5cd9670018dc61a8640fb9fef2))

## [1.19.8](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.19.7...v1.19.8) (2024-08-05)


### Bug Fixes

* **table:** do not filter unsupported results ([c5be423](https://gitlab.laas.fr/rgodet1/tyr/commit/c5be4234eb8f93c2ab39b9ddaad8fec84e92b8c7))
* **table:** final row with multiple columns ([f52d59c](https://gitlab.laas.fr/rgodet1/tyr/commit/f52d59c68a91f2d586e4e2be0f07a98b0203c7a9))

## [1.19.7](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.19.6...v1.19.7) (2024-08-02)


### Bug Fixes

* **domains:** aaai25 empty plan quality for drone and counters ([9b12585](https://gitlab.laas.fr/rgodet1/tyr/commit/9b12585f4c6e157913d375d68ef4953b6218ef18))

## [1.19.6](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.19.5...v1.19.6) (2024-08-01)


### Bug Fixes

* **planners:** catch errors and handle writer as output_stream for PDDL planners ([2bb8b7e](https://gitlab.laas.fr/rgodet1/tyr/commit/2bb8b7e5582b44a87b4ee4d820c2f581aff6f0f2))
* **planners:** ensure log file creation ([1617771](https://gitlab.laas.fr/rgodet1/tyr/commit/1617771bc1bb2211e6cb8fbdcd9dfbfaab71eb77))
* **planners:** filter timeout results in anytime ([b2af334](https://gitlab.laas.fr/rgodet1/tyr/commit/b2af33488190897c72b639718a960aa8e5d96412))
* **planners:** timeout on self stopped process without plan ([896b4b6](https://gitlab.laas.fr/rgodet1/tyr/commit/896b4b6915e8ffcf1dd431146b3dfc1909c6c08b))
* **table:** load empty config ([af9a016](https://gitlab.laas.fr/rgodet1/tyr/commit/af9a01636c8ecc2c228c3b17728880daacd0808d))

## [1.19.5](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.19.4...v1.19.5) (2024-07-31)


### Bug Fixes

* **planners:** use multiprocessing to force the timeout ([3b8627b](https://gitlab.laas.fr/rgodet1/tyr/commit/3b8627bb0e1c62ecba3ea25c9f9d9cf7965c8cce))

## [1.19.4](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.19.3...v1.19.4) (2024-07-31)


### Bug Fixes

* **pddl:** use a clone of the original action to preserve original cost ([8a48938](https://gitlab.laas.fr/rgodet1/tyr/commit/8a489385328e92905819a7359f41231e6f491312))
* **planners:** pddl and apptainer plan parsing ([0d5f88e](https://gitlab.laas.fr/rgodet1/tyr/commit/0d5f88ef951cb8b32ff0ba8e7cb30875ce3f1a25))
* **planners:** save output of PDDL planners in logs ([68b527a](https://gitlab.laas.fr/rgodet1/tyr/commit/68b527a43a2c8eb496cbc0a33b5ada439a92e72a))

## [1.19.3](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.19.2...v1.19.3) (2024-07-31)


### Bug Fixes

* **cli:** add GRPC_VERBOSITY env to aries in order to silence grpc warning ([1305f8f](https://gitlab.laas.fr/rgodet1/tyr/commit/1305f8f6f5018c8b401a712456311681bcbc0ef5))

## [1.19.2](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.19.1...v1.19.2) (2024-07-30)


### Bug Fixes

* **logs:** catch errors on log export ([21053a4](https://gitlab.laas.fr/rgodet1/tyr/commit/21053a44e0079b06f4825191529f74efcc0ac57d))

## [1.19.1](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.19.0...v1.19.1) (2024-07-29)

# [1.19.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.18.0...v1.19.0) (2024-07-27)


### Bug Fixes

* **just:** panda-pi registration ([4aab468](https://gitlab.laas.fr/rgodet1/tyr/commit/4aab4680f282860c84ee4b28f3a4a5674dd14663))
* popcorn submodule url ([fd2ba92](https://gitlab.laas.fr/rgodet1/tyr/commit/fd2ba921cc5fe646c97e5fdf359ad37b77bb29ae))
* **problem:** makespan computation for non temporal problem but time triggered plan ([7363098](https://gitlab.laas.fr/rgodet1/tyr/commit/7363098d7a4626f41f26ae8fb34d0678ee0c20fb))
* **problems:** calculate action cost of plan ([4a0e812](https://gitlab.laas.fr/rgodet1/tyr/commit/4a0e8127cd5728ee8c03d4b05d798d25a1cc72c3))
* **result:** check problem is temporal before unify epsilons ([0a77991](https://gitlab.laas.fr/rgodet1/tyr/commit/0a77991029dcc17340dc83b000071e32be3d573f))


### Features

* **bench:** can unify temporal epsilon ([2a59e5b](https://gitlab.laas.fr/rgodet1/tyr/commit/2a59e5b6d5b872b53c67ab98e5cba443d86fcf2e))
* **converter:** new one to remove user typing ([44426f4](https://gitlab.laas.fr/rgodet1/tyr/commit/44426f420a062fef5158667caa9076b3dc94cdb7))
* **domains:** add ipc submodule ([4306578](https://gitlab.laas.fr/rgodet1/tyr/commit/4306578c8b5f8fe537732aa540e4b83dddba2289))
* **planners:** add popcorn ([72e6e69](https://gitlab.laas.fr/rgodet1/tyr/commit/72e6e696564f24ae8cdaf2bee7674cbc0db3b1d5))
* **planners:** add tamer ([4d9e461](https://gitlab.laas.fr/rgodet1/tyr/commit/4d9e461229acdfd8607db990b8fedb66b66e09af))
* **problems:** calculate action cost of plan ([0506b7c](https://gitlab.laas.fr/rgodet1/tyr/commit/0506b7c60c2bc4fa943355f56d7c7d39e4fa5eb1))


### Reverts

* **docker:** remove apptainer ([c80392f](https://gitlab.laas.fr/rgodet1/tyr/commit/c80392fb4a7ca65a2640e788a2b0d53c233ddc71))

# [1.18.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.17.0...v1.18.0) (2024-06-21)


### Bug Fixes

* **apptainer:** install java ([dc28883](https://gitlab.laas.fr/rgodet1/tyr/commit/dc28883fba381a6c3d7fb14f416c77f8ebf10370))
* **cli:** merge int options ([27e7e38](https://gitlab.laas.fr/rgodet1/tyr/commit/27e7e3829b7378db3f14906381360f72974dce6c))
* **database:** add a security offset when loading previous results of the same run ([bcb5ddb](https://gitlab.laas.fr/rgodet1/tyr/commit/bcb5ddb345a1db124a247ce22e6df7d6448715d9))
* **database:** for anytime, try to get the latest result before the timeout ([c8b9f03](https://gitlab.laas.fr/rgodet1/tyr/commit/c8b9f0336d07a1dadf04bd1c2129d50f58b5a35a))
* **database:** retry on in/out error during saving ([67bdded](https://gitlab.laas.fr/rgodet1/tyr/commit/67bdded0caab13a93624e007f790c515049a84f5))
* **database:** try to get the latest solved result of the run in anytime ([fdd2ea8](https://gitlab.laas.fr/rgodet1/tyr/commit/fdd2ea897faabe20ccfaa70fd4350871a77b188f))
* **database:** use multiprocessing to save results ([0de0565](https://gitlab.laas.fr/rgodet1/tyr/commit/0de0565ab8493147f994b98e3dde9c72593e0a4f))
* **domains:** rover and satellite quality with timed plans ([9bbdfb6](https://gitlab.laas.fr/rgodet1/tyr/commit/9bbdfb63108128a9ec39e03a8d55e3dda1e5ae4f))
* **domains:** specify version name to get the quality ([8a4f518](https://gitlab.laas.fr/rgodet1/tyr/commit/8a4f518b4ac8acc20815b53b09dd50bb8341d715))
* **lpg:** detect timeout from logs ([f13dd3e](https://gitlab.laas.fr/rgodet1/tyr/commit/f13dd3e31acff78279efd8cd7e0203531e50fb3c))
* **metric:** best quality score of zero ([0822993](https://gitlab.laas.fr/rgodet1/tyr/commit/0822993b32bbff5ddb29109d832148b15bec8b9c))
* **metric:** stop filtering resutls ([25a1422](https://gitlab.laas.fr/rgodet1/tyr/commit/25a14220b6cc480d2f0546b3405c60d49512925c))
* **optic:** cmd option position ([293a414](https://gitlab.laas.fr/rgodet1/tyr/commit/293a414b482c0332572100a1cae9cfe5d1ebf7b3))
* **optic:** get several plans in anytime mode ([c657694](https://gitlab.laas.fr/rgodet1/tyr/commit/c657694fabb82478944cab23d703bc5a0d6c59af))
* **optic:** get the latest plan ([485668d](https://gitlab.laas.fr/rgodet1/tyr/commit/485668d651b720785f7f3e340bab2589161e6667))
* **optic:** get the latest plan from the logs ([458ef62](https://gitlab.laas.fr/rgodet1/tyr/commit/458ef62b6355306a1467d1598f6df4c357e4ec86))
* **optic:** plan detection ([c7e76f2](https://gitlab.laas.fr/rgodet1/tyr/commit/c7e76f2390ef3f4cab2b7df73ecd7db569ea735e))
* **optic:** plan detection when no end line ([b1c8af1](https://gitlab.laas.fr/rgodet1/tyr/commit/b1c8af147403776ab3ec841c00f593bdb8b4b8c4))
* **optic:** status when plan is empty ([7c03f12](https://gitlab.laas.fr/rgodet1/tyr/commit/7c03f121e652f70fd121845558483f58ecf2be3c))
* **planner:** disable timeout alarm on error ([97a53f4](https://gitlab.laas.fr/rgodet1/tyr/commit/97a53f4846c3e2e578f077eb7967a9b38c843bff))
* **planners:** process killing ([a46821e](https://gitlab.laas.fr/rgodet1/tyr/commit/a46821e34141a7a0345833a1766b33bca54201af))
* **planners:** save local planner name instead of upf one in the database ([9acf05e](https://gitlab.laas.fr/rgodet1/tyr/commit/9acf05e9f74dddddca21266f9add40b1604572d0))
* **planners:** status when no plan ([20eaf63](https://gitlab.laas.fr/rgodet1/tyr/commit/20eaf63b889b02193456cbf345385b9668f008a7))
* **planners:** use red_no_float version for satellite numeric ([ea46a08](https://gitlab.laas.fr/rgodet1/tyr/commit/ea46a0825534cea519a8c2049bf4cfd1b6f677fa))
* **planner:** wrap whole solving code in try/except ([0dcaba2](https://gitlab.laas.fr/rgodet1/tyr/commit/0dcaba2914e6f0d7d8ec53412a323eb47c16ed35))
* **plot:** quality ratio basis value in latex export ([6a74a36](https://gitlab.laas.fr/rgodet1/tyr/commit/6a74a36a18343ebfc8dfbb9e9d3035da66ecdfef))
* **plot:** use only anytime results for quality ratio ([cf9bf8e](https://gitlab.laas.fr/rgodet1/tyr/commit/cf9bf8edf301e0e101d80fad07a232d273a9ed72))
* **popf:** empty plan detection ([eef0a49](https://gitlab.laas.fr/rgodet1/tyr/commit/eef0a49cb5bea2db13847704545996ea6d85ef67))
* **problems:** check integer fluent bounds when convert sched to actions ([01f40c9](https://gitlab.laas.fr/rgodet1/tyr/commit/01f40c9a1b02a152c753779bd1901eaa2588ddc5))
* **rovers:** quality of numerical plans ([7e41cf3](https://gitlab.laas.fr/rgodet1/tyr/commit/7e41cf3917d050052820b7dfa7fe7dbef7f320a1))
* **satellite:** quality of numerical plans ([9339723](https://gitlab.laas.fr/rgodet1/tyr/commit/9339723dcb5a557680cf916c92dcca7002c719e8))
* **scheduling:** constraint creation ([77ad027](https://gitlab.laas.fr/rgodet1/tyr/commit/77ad02757ac13759abb0f6124851abad58ca6d40))
* **slurm:** specify min and max number of nodes ([516895f](https://gitlab.laas.fr/rgodet1/tyr/commit/516895f5dedf444d405713033fa622d8c07272f3))
* **slurm:** use dedicated db for each task ([89f707a](https://gitlab.laas.fr/rgodet1/tyr/commit/89f707a4e57bdd7129f6599ca2f8b8dd94a27a8d))
* **table:** give col headers to latex ([7a685bd](https://gitlab.laas.fr/rgodet1/tyr/commit/7a685bde8e8f68962ce86a5d82637aef15aafea0))
* **table:** headers can have different number of subheaders ([78dc34d](https://gitlab.laas.fr/rgodet1/tyr/commit/78dc34da30dff410ecb2e1b68465b52cf989caf8))
* **table:** intermediate horizontal dashed separator in latex ([21c5839](https://gitlab.laas.fr/rgodet1/tyr/commit/21c5839384f5154eb24adbbfbe85b17aa43f3aa0))
* **table:** latex horizontal separators ([e4070fd](https://gitlab.laas.fr/rgodet1/tyr/commit/e4070fde3f865c6d906d761c9b6c68e619f331bc))
* **table:** latex horizontal separators of unit size ([2c792f9](https://gitlab.laas.fr/rgodet1/tyr/commit/2c792f9361df00b9a99f64e88e7cf823453cd376))
* **table:** latex separator over domains ([38fa5f9](https://gitlab.laas.fr/rgodet1/tyr/commit/38fa5f92ed77ea692a51ade553f1177fd118a5cd))
* **table:** vertical terminal separator ([899b53f](https://gitlab.laas.fr/rgodet1/tyr/commit/899b53fdbde96800d54a030737799c0e791dd510))


### Features

* **cli:** in quiet mode, the header is not printed ([bec09a6](https://gitlab.laas.fr/rgodet1/tyr/commit/bec09a6b71e882a6eade4ea627cdfaa385103d7c))
* **cli:** print the timeout offset ([d4617d4](https://gitlab.laas.fr/rgodet1/tyr/commit/d4617d4c730e6abc42971c37781eb6056e4801e2))
* **metrics:** add quality ratio ([f4cc390](https://gitlab.laas.fr/rgodet1/tyr/commit/f4cc39039022ba221a4904325e62ad4faec6738f))
* **metrics:** add relative quality score ([5f970c8](https://gitlab.laas.fr/rgodet1/tyr/commit/5f970c856da9a00a57848b3b380e9b4631169986))
* **optic:** get all intermediate plans ([8eea161](https://gitlab.laas.fr/rgodet1/tyr/commit/8eea161bd1f33baccc73f8a555a9b333c7fdb64c))
* **pddl planners:** can get computation time from logs ([a4b7f66](https://gitlab.laas.fr/rgodet1/tyr/commit/a4b7f66c063cf73f108e9befd27f810cadc3bc36))
* **planners:** add additional offset seconds before force planner to timeout ([6b38bdd](https://gitlab.laas.fr/rgodet1/tyr/commit/6b38bdda9b21e5222c525baa1ac8f1c08292b2dd))
* **planners:** add ENHSP ([fbd8b6f](https://gitlab.laas.fr/rgodet1/tyr/commit/fbd8b6f0279133fd56bdfc8988112eacde49927d))
* **planners:** add POPF ([7c9ef92](https://gitlab.laas.fr/rgodet1/tyr/commit/7c9ef922d9dc1fa2d85031b38d8e9d3d3a6b107e))
* **result:** can be merged ([1d9bd89](https://gitlab.laas.fr/rgodet1/tyr/commit/1d9bd89f672871e41c51cfca84f0b44d6459403e))
* **script:** merge SQLite database files into a single database ([29a071d](https://gitlab.laas.fr/rgodet1/tyr/commit/29a071dc01ba057be371ee12ac1184876ffa7e26))
* **singleton:** methods for clearing and purging instances ([66fc48c](https://gitlab.laas.fr/rgodet1/tyr/commit/66fc48c19752b496e33ec3c30fd4b23a72923d77))
* **table:** add latex-star option to create a table* ([2c3ebf0](https://gitlab.laas.fr/rgodet1/tyr/commit/2c3ebf0de73bf59d8d386578f43638c4812b7d2d))
* **table:** can add final row and column ([9c8346b](https://gitlab.laas.fr/rgodet1/tyr/commit/9c8346bf017e08e91f3aecb32e0d6f8e129dd12a))
* **table:** can specify latex font size ([850075f](https://gitlab.laas.fr/rgodet1/tyr/commit/850075fdf84ecc8efc01664e855252207402b5a7))
* **table:** can specify latex position ([a706241](https://gitlab.laas.fr/rgodet1/tyr/commit/a7062419aab3bf7c8ea4d7acc35140e12076ca8d))
* **table:** can specify latex vertical and horizontal spaces ([05ca21c](https://gitlab.laas.fr/rgodet1/tyr/commit/05ca21c0fc6ec7ed2e6b8dc6c0655cdeacc76c24))
* **table:** filter candidates with unsupported results ([dcd5e7f](https://gitlab.laas.fr/rgodet1/tyr/commit/dcd5e7f2d873b58efce810e51a200d0fc565660b))
* **table:** merge results ([278c913](https://gitlab.laas.fr/rgodet1/tyr/commit/278c9131b8c9231c60645f6b6e3ae8060f22ca83))


### Reverts

* **planner:** stop anytime first solution duplication ([8f9f153](https://gitlab.laas.fr/rgodet1/tyr/commit/8f9f15390ef6fb395903e9a2e73e55840dc53200))

# [1.17.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.16.0...v1.17.0) (2024-04-09)


### Features

* **planners:** duplicate first anytime result as oneshot ([61d9c4b](https://gitlab.laas.fr/rgodet1/tyr/commit/61d9c4b476d0e088ceef9ccdf233c53ad6721964))
* **planners:** return all results ([9f6991f](https://gitlab.laas.fr/rgodet1/tyr/commit/9f6991fe7939fb0d97bcb7c6cf365e539f3fd4c3))

# [1.16.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.15.0...v1.16.0) (2024-04-06)


### Features

* **planners:** upf engine can be specified in the config file ([2df3287](https://gitlab.laas.fr/rgodet1/tyr/commit/2df3287bc42c721f3e46675a6ca03aaaeebcf522))

# [1.15.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.14.0...v1.15.0) (2024-04-05)


### Bug Fixes

* **apptainer:** remove non example configuration files and install apptainer ([0fb583a](https://gitlab.laas.fr/rgodet1/tyr/commit/0fb583a4aea9e47413658e66dbb97048a6145853))
* **slurm:** domain index computation ([086db47](https://gitlab.laas.fr/rgodet1/tyr/commit/086db472c7f01fa9ddb9a720684c517aa6a4294e))
* **slurm:** sif location ([baed91d](https://gitlab.laas.fr/rgodet1/tyr/commit/baed91da7c84c8a81a7304f67cce2bbc8cbef0e2))
* **tests:** disable potential planner timeout signal ([5309b27](https://gitlab.laas.fr/rgodet1/tyr/commit/5309b27bb2f7aa853f98cc0248a7bfc269a7d3b3))


### Features

* **cli:** add slurm cmd ([322b398](https://gitlab.laas.fr/rgodet1/tyr/commit/322b398ebbcc735e45b33baf8e80a6d72197172c))
* **cli:** can specify db and logs paths ([bf19e96](https://gitlab.laas.fr/rgodet1/tyr/commit/bf19e961d7fbecf6566c821117195077f85ec794))
* **cli:** distinction between no-db-load and no-db-save ([8652f38](https://gitlab.laas.fr/rgodet1/tyr/commit/8652f38f9761c66c249529ba27ebf933eb1809f0))
* **pattern:** singleton can have a post_init method ([82229a0](https://gitlab.laas.fr/rgodet1/tyr/commit/82229a0eaad886c8d77af634c19a42baab5c7022))


### Reverts

* **cli:** disable chaining ([c46c9b6](https://gitlab.laas.fr/rgodet1/tyr/commit/c46c9b6675541068218edeaeeeaee09570e191ea))

# [1.14.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.13.0...v1.14.0) (2024-03-26)


### Bug Fixes

* **database:** bigger timeout detection ([f0388c7](https://gitlab.laas.fr/rgodet1/tyr/commit/f0388c7d6fb120f031b32e5a6df2ebf0cf0b2c1b))
* **database:** loading not run results returns None ([b7bd8af](https://gitlab.laas.fr/rgodet1/tyr/commit/b7bd8afe664f01a848225ee7f735dd9f4cdb7e84))
* **database:** return None if result is timeout and config has a bigger one ([15a7767](https://gitlab.laas.fr/rgodet1/tyr/commit/15a776764fcb2552bf3b2668a8aa59d97bc7667b))
* **domains:**  insertion version of goto-simple domain ([8c1db0d](https://gitlab.laas.fr/rgodet1/tyr/commit/8c1db0d120b90b445f1b63a963bac458f07a6463))
* **domains:** goto-complex and hard number of goals ([f8c62d6](https://gitlab.laas.fr/rgodet1/tyr/commit/f8c62d6b447f7a931a1bf96a9c2007be47f0097f))
* **metric:** filter not_run, error, and unsupported ([3273da0](https://gitlab.laas.fr/rgodet1/tyr/commit/3273da00895331488dd76f52607732c3c158d9e2))
* **planner:** detect memout based on logs ([d73f48d](https://gitlab.laas.fr/rgodet1/tyr/commit/d73f48d0b10cb80065571e42ad1945f8f61216e9))
* **planners:** planner name in result was based on upf engine name ([b99e066](https://gitlab.laas.fr/rgodet1/tyr/commit/b99e066de26531cb6061f7f030004bdb4aaf86dd))
* **plotters:** sum times for cactus and survival ([7f480be](https://gitlab.laas.fr/rgodet1/tyr/commit/7f480bea17865f1668ef835b3991fa048d46e09e))
* **table:** order columns ([d3de96b](https://gitlab.laas.fr/rgodet1/tyr/commit/d3de96b8994cfc13f29690eb0a8cd6a1644eb274))
* **test:** specify metric mock's abbreviation ([18f0751](https://gitlab.laas.fr/rgodet1/tyr/commit/18f0751273b23c3ab871fe2af5a27c2f260104df))


### Features

* **analyse:** add best footer and column ([3754e82](https://gitlab.laas.fr/rgodet1/tyr/commit/3754e8246324f791077681f2f537484d0a38986f))
* **analyse:** can disable best row and col ([3c9bde3](https://gitlab.laas.fr/rgodet1/tyr/commit/3c9bde3885f52696754a98b0190e759d8d843008))
* **analyse:** can order planners, metrics, domains and categories ([864fde6](https://gitlab.laas.fr/rgodet1/tyr/commit/864fde6034531f7d75500fd0eefccc8f2847313c))
* **analyse:** filter not run problems and check unsupported consistency ([b09b9ee](https://gitlab.laas.fr/rgodet1/tyr/commit/b09b9ee530cd27ce9c8723c844a8c81e156446e3))
* **analyse:** mapping for domain, planner, and add categories ([16ebd04](https://gitlab.laas.fr/rgodet1/tyr/commit/16ebd04d0bbe9631ea408ccf708b6b386250f0a2))
* **analyse:** show the number of instances in a domain ([8be64c6](https://gitlab.laas.fr/rgodet1/tyr/commit/8be64c6d2cd585f5aa4778803f1356cb18db2341))
* **cli:** add analyse command ([8eee482](https://gitlab.laas.fr/rgodet1/tyr/commit/8eee48232cc6ca0706dcf3fa1aa88f7ea4f54fa8))
* **cli:** add plot command ([5681d87](https://gitlab.laas.fr/rgodet1/tyr/commit/5681d871220cbd7fab757992e617f4cc06692ba6))
* **cli:** can chain commands ([a3ef91a](https://gitlab.laas.fr/rgodet1/tyr/commit/a3ef91a5f96b839ba7842d80f520ee511d1c8e06))
* **cli:** can export table in LaTeX ([b1a245f](https://gitlab.laas.fr/rgodet1/tyr/commit/b1a245f906e7b4e8e7b94293565abb08c0c43991))
* **cli:** can group cell vertical in table ([920125f](https://gitlab.laas.fr/rgodet1/tyr/commit/920125f5907acb8ba0ff0e6000292badedcd1dec))
* **cli:** can specify caption of latex table ([a22cc2b](https://gitlab.laas.fr/rgodet1/tyr/commit/a22cc2b0e4d647d28f735aa8bdbebed4eb6ccb4a))
* **cli:** headers of the table are more customizable ([0096b99](https://gitlab.laas.fr/rgodet1/tyr/commit/0096b992fbaff7f6f31f65f0b6ae2b6550aeb30d))
* **collector:** collect metrics ([9de17b8](https://gitlab.laas.fr/rgodet1/tyr/commit/9de17b8e6a2b7d0584b9d2ca7096881632047665))
* **database:** can keep unsupported results ([3b85f8a](https://gitlab.laas.fr/rgodet1/tyr/commit/3b85f8aa8fdd8cad66abd94823e259b1a790015f))
* **domains:** add complex and hard goto ([fa7f682](https://gitlab.laas.fr/rgodet1/tyr/commit/fa7f68293b627e86f4693b464dc5fd69fbf0007d))
* **domains:** add Factories Simple ([d7a446e](https://gitlab.laas.fr/rgodet1/tyr/commit/d7a446ead71890c992ae8776aa4c4b1d7b11e4ea))
* **domains:** add instance 31-40 for gotos, with 1-10 goto tasks ([99bb90a](https://gitlab.laas.fr/rgodet1/tyr/commit/99bb90a61b397851fd9dcb66e08329fcbf5b8904))
* **domains:** add rovers versions ([a898fb1](https://gitlab.laas.fr/rgodet1/tyr/commit/a898fb105c8c08920d878bdd8634f6d018050f97))
* **domains:** add simple goto in base and linear versions ([e9be1a5](https://gitlab.laas.fr/rgodet1/tyr/commit/e9be1a53b359fc1ffc7a61c00d8dec524bce732b))
* **domains:** add task insertion version of simple goto ([4cd8b02](https://gitlab.laas.fr/rgodet1/tyr/commit/4cd8b02d183484a7da3c02955ae2b8fab2b67ed8))
* **domains:** add transport ([402bb0f](https://gitlab.laas.fr/rgodet1/tyr/commit/402bb0fe2f6ba1684e67492390c9f8324a5ab0bb))
* **domains:** add versions for transport ([6a582e3](https://gitlab.laas.fr/rgodet1/tyr/commit/6a582e395fedd196eb5aaca8a180cf7b92a26a64))
* **metrics:** add quality score ([204dfa2](https://gitlab.laas.fr/rgodet1/tyr/commit/204dfa21a7e01362a166fe1e635b889f4cbc29ad))
* **metrics:** creation ([2dc6583](https://gitlab.laas.fr/rgodet1/tyr/commit/2dc65833be5cf3f8967e2ac51f377a79ff445717))
* **pddl planner:** can override the temporary file extension ([def5a8a](https://gitlab.laas.fr/rgodet1/tyr/commit/def5a8a5b65b1275ccdbf7fdd614db1a43ef9748))
* **planners:** add aries-linear version for simple-goto ([1d203c5](https://gitlab.laas.fr/rgodet1/tyr/commit/1d203c55a0543c7aaf37082a5d1c54b28dc644fe))
* **planners:** add exponential versions for aries, linear and panda-pi ([61d3383](https://gitlab.laas.fr/rgodet1/tyr/commit/61d3383d8e612e5238f1c062c764a46cb817cbd1))
* **planners:** add linear planner, winner of ipc-23 ([baaace1](https://gitlab.laas.fr/rgodet1/tyr/commit/baaace1fc9a11fed84e12d132ace32a3086fe461))
* **planners:** add PandaPi planner linear version ([2a78d56](https://gitlab.laas.fr/rgodet1/tyr/commit/2a78d56c3c76273d80f0fd6be9545b83246d9c7a))
* **planners:** create generic singularity planner ([bd7fd69](https://gitlab.laas.fr/rgodet1/tyr/commit/bd7fd6951bffc52b296e4fd6ea1502646f119091))
* **planners:** get makespan of hierarchical plans ([f203d10](https://gitlab.laas.fr/rgodet1/tyr/commit/f203d105c37e4ca5f515989a6e462eec86e74a6e))
* **planner:** use makespan if no metric is specified ([a426eea](https://gitlab.laas.fr/rgodet1/tyr/commit/a426eea20b855e3911cc6c701b57a1948307d1e1))
* **plotters:** add CDF ([d883599](https://gitlab.laas.fr/rgodet1/tyr/commit/d883599b3ed179205598dab719f73fd3cbd82a56))
* **plotters:** add reversed cdf plot ([b99f54d](https://gitlab.laas.fr/rgodet1/tyr/commit/b99f54da8e5d8cfa43238b661b39ac45d352746a))
* **plotters:** cactus and survival ([b9982a6](https://gitlab.laas.fr/rgodet1/tyr/commit/b9982a60b199ec25b7e236a89149c967b6b62341))
* **plotters:** can export in latex ([54b7b0c](https://gitlab.laas.fr/rgodet1/tyr/commit/54b7b0c0710e33812d2920d9b431aaaf275db0a4))
* **table:** can select metrics by abbreviation ([fdb3be6](https://gitlab.laas.fr/rgodet1/tyr/commit/fdb3be61d49d53a8918f631a13cf84b24e420f66))


### Reverts

* hddl-writter branch of upf has been merged into master ([af0c26b](https://gitlab.laas.fr/rgodet1/tyr/commit/af0c26b080e43f6fe5f9d1d60e983a5b61e21241))

# [1.13.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.12.0...v1.13.0) (2024-03-19)


### Bug Fixes

* **database:** null computation time compared with timeout ([79d2bb5](https://gitlab.laas.fr/rgodet1/tyr/commit/79d2bb5ef5e17b1b4c91755f942c51d8e82f282c))


### Features

* **cli:** add quiet option ([93e92fc](https://gitlab.laas.fr/rgodet1/tyr/commit/93e92fca04b7a10ac73fd4b23e01de7e5ac8beaa))
* **database:** return none if last result was unsupported ([3cff95f](https://gitlab.laas.fr/rgodet1/tyr/commit/3cff95f4d438f95d62cd4c40366f978523a542f1))


### Performance Improvements

* **planner:** check database before getting the version ([dc39bb2](https://gitlab.laas.fr/rgodet1/tyr/commit/dc39bb27ab45afc544a0c67053695ffdae9ddb17))

# [1.12.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.11.0...v1.12.0) (2024-03-14)


### Bug Fixes

* **cli:** convert timeout, memout and jobs into int ([b1a6271](https://gitlab.laas.fr/rgodet1/tyr/commit/b1a6271fe5f1666982ab893328339e4c0c02cf44))
* **planners:** kill the process if still running ([c623e90](https://gitlab.laas.fr/rgodet1/tyr/commit/c623e903276b3ee0e07b24a311612cb588a52cb8))


### Features

* **planners:** add PandaPi ([873d37d](https://gitlab.laas.fr/rgodet1/tyr/commit/873d37d13d677f991358cae31c6b5fd6bc95b3df))

# [1.11.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.10.1...v1.11.0) (2024-03-12)


### Features

* **cli:** can specify a specific config file ([4ed8d9d](https://gitlab.laas.fr/rgodet1/tyr/commit/4ed8d9d79283a0fc1c7f17e23393ca9323dde259))
* **cli:** display the used config file ([7e8049c](https://gitlab.laas.fr/rgodet1/tyr/commit/7e8049cc07efe9d6a13b8425f0bfea9083daee4c))
* **cli:** get argument values from config file before cli values ([b04b255](https://gitlab.laas.fr/rgodet1/tyr/commit/b04b25526c97e66f942d51759ad231df59fc1403))
* **config:** add config loader ([4d3213d](https://gitlab.laas.fr/rgodet1/tyr/commit/4d3213d9ad1f819dc652e4b0a7ef70cb3ab5df8c))
* **config:** can specify the full path of the configuration file to the loader ([e72597c](https://gitlab.laas.fr/rgodet1/tyr/commit/e72597ceb74e2d4caa4fd37049672c3465bc543b))
* **config:** load example file if local is not present ([0628ccd](https://gitlab.laas.fr/rgodet1/tyr/commit/0628ccdb2e0c0cc757ba44870c8537eff850a224))

## [1.10.1](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.10.0...v1.10.1) (2024-03-12)


### Bug Fixes

* **database:** do not save results from the database again ([58cf507](https://gitlab.laas.fr/rgodet1/tyr/commit/58cf507c9e7a78d1a2bd63a7cd8a55964bc32654))

# [1.10.0](https://gitlab.laas.fr/rgodet1/tyr/compare/v1.9.0...v1.10.0) (2024-03-12)


### Bug Fixes

* **planner:** detection of timeout in anytime which is in reality a solve ([66fc609](https://gitlab.laas.fr/rgodet1/tyr/commit/66fc60917dce2178d195ccee7a6963ec22c3fee4))
* **planners:** timeout for anytime mode ([e6b6e44](https://gitlab.laas.fr/rgodet1/tyr/commit/e6b6e44b4e46503c645fa67d6b4e1059890e8397))


### Features

* **cli:** always save results in the database ([f3dd215](https://gitlab.laas.fr/rgodet1/tyr/commit/f3dd21577cdf7f68afe686da2a8205504696f907))
* **cli:** can force or disable the database ([a6c9db6](https://gitlab.laas.fr/rgodet1/tyr/commit/a6c9db615f87814f8e94027afcdec60f3c5be288))
* **cli:** display error and plan logs for solve command ([e636210](https://gitlab.laas.fr/rgodet1/tyr/commit/e636210f4f2162946fc8ba8014a3d43040ced715))
* **cli:** display if the result comes from the database ([b0182f1](https://gitlab.laas.fr/rgodet1/tyr/commit/b0182f167c09b26bbab4b9dd18cce34119f4bf4d))
* **database:** load the last result with optional timeout if needed ([f2811da](https://gitlab.laas.fr/rgodet1/tyr/commit/f2811da1bcaa1d461c2dcdd40e78f9f8350c7fdd))
* **db:** save solve config in database ([adb3716](https://gitlab.laas.fr/rgodet1/tyr/commit/adb3716e18c5954e7523699b43b5bcea9c20489e))
* **planner:** add str representation ([8672e0c](https://gitlab.laas.fr/rgodet1/tyr/commit/8672e0c3c3b3b041a466bd28e75fd1787d046998))
* **planner:** save plan in logs ([dfbec08](https://gitlab.laas.fr/rgodet1/tyr/commit/dfbec08e5fe15809e5f9774aca2843858c5c6dfc))

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
