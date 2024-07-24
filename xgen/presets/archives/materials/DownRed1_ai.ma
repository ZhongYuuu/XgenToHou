//Maya ASCII 2017ff03 scene
//Name: DownRed1_ai.ma
//Last modified: Tue, Mar 15, 2016 02:37:42 PM
//Codeset: 1252
requires maya "2017ff03";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2017";
fileInfo "version" "Preview Release 64";
fileInfo "cutIdentifier" "201603150300-989850-2";
fileInfo "osv" "Microsoft Windows 7 Ultimate Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode transform -n "paintfx_archives:downRed1ShaderSG_materialRef";
	rename -uid "EA479FD7-4C81-C857-D160-739BB9F49A49";
createNode mesh -n "paintfx_archives:downRed1ShaderSG_materialRefShape" -p "paintfx_archives:downRed1ShaderSG_materialRef";
	rename -uid "DB889993-4B11-8C76-CA15-EE9BA9899B6F";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.375 0 0.625 0 0.375
		 0.25 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.375 1 0.625 1 0.875 0
		 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 8 ".vt[0:7]"  0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0;
	setAttr -s 12 ".ed[0:11]"  0 1 0 2 3 0 4 5 0 6 7 0 0 2 0 1 3 0 2 4 0
		 3 5 0 4 6 0 5 7 0 6 0 0 7 1 0;
	setAttr -s 6 -ch 24 ".fc[0:5]" -type "polyFaces" 
		f 4 0 5 -2 -5
		mu 0 4 0 1 3 2
		f 4 1 7 -3 -7
		mu 0 4 2 3 5 4
		f 4 2 9 -4 -9
		mu 0 4 4 5 7 6
		f 4 3 11 -1 -11
		mu 0 4 6 7 9 8
		f 4 -12 -10 -8 -6
		mu 0 4 1 10 11 3
		f 4 10 4 6 8
		mu 0 4 12 0 2 13;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
	setAttr ".ndt" 0;
	setAttr ".ai_translator" -type "string" "polymesh";
createNode transform -n "paintfx_archives:downRed1LeafShaderSG_materialRef";
	rename -uid "047D9807-4E0D-A51F-6CF0-0FAEB17397A4";
createNode mesh -n "paintfx_archives:downRed1LeafShaderSG_materialRefShape" -p "paintfx_archives:downRed1LeafShaderSG_materialRef";
	rename -uid "01B19304-408E-7618-E879-3CAE7D2A345B";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.375 0 0.625 0 0.375
		 0.25 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.375 1 0.625 1 0.875 0
		 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 8 ".vt[0:7]"  0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0;
	setAttr -s 12 ".ed[0:11]"  0 1 0 2 3 0 4 5 0 6 7 0 0 2 0 1 3 0 2 4 0
		 3 5 0 4 6 0 5 7 0 6 0 0 7 1 0;
	setAttr -s 6 -ch 24 ".fc[0:5]" -type "polyFaces" 
		f 4 0 5 -2 -5
		mu 0 4 0 1 3 2
		f 4 1 7 -3 -7
		mu 0 4 2 3 5 4
		f 4 2 9 -4 -9
		mu 0 4 4 5 7 6
		f 4 3 11 -1 -11
		mu 0 4 6 7 9 8
		f 4 -12 -10 -8 -6
		mu 0 4 1 10 11 3
		f 4 10 4 6 8
		mu 0 4 12 0 2 13;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
	setAttr ".ndt" 0;
	setAttr ".ai_translator" -type "string" "polymesh";
createNode shadingEngine -n "paintfx_archives:downRed1ShaderSG";
	rename -uid "62F15F34-4261-7FEA-D9CE-7595AFBAB2DD";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
createNode shadingEngine -n "paintfx_archives:downRed1LeafShaderSG";
	rename -uid "18A8A29A-45E0-1166-80F0-73BE3FA46C05";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
createNode materialInfo -n "paintfx_archives:materialInfo20";
	rename -uid "4C38669A-49A3-2F7E-8D5D-DA854A902674";
createNode phong -n "paintfx_archives:downRed1Shader";
	rename -uid "A05B1CD8-437B-B581-BBBC-769BE4ADBE50";
	setAttr ".dc" 0.23299999535083771;
	setAttr ".tc" 0.76700001955032349;
	setAttr ".tcf" 0;
	setAttr ".trsd" 1;
	setAttr ".fakc" 0;
	setAttr ".sc" -type "float3" 0.43434039 0.099828236 0.15937491 ;
	setAttr ".cp" 2.3299999237060547;
createNode ramp -n "paintfx_archives:ramp20";
	rename -uid "B42DF9A1-473E-ADD3-0488-5498EB5DFE28";
	setAttr -s 2 ".cel";
	setAttr ".cel[0].ep" 0;
	setAttr ".cel[0].ec" -type "float3" 0.65053397 0.39484459 0.36662138 ;
	setAttr ".cel[1].ep" 1;
	setAttr ".cel[1].ec" -type "float3" 1 0.074509807 0 ;
createNode materialInfo -n "paintfx_archives:materialInfo21";
	rename -uid "62169261-484E-0C24-B28E-509CD0B7FB1E";
createNode phong -n "paintfx_archives:downRed1LeafShader";
	rename -uid "63458B6E-4A71-BA06-060B-F3B5ABDDD7D8";
	setAttr ".dc" 0.24271999299526215;
	setAttr ".tc" 0.75727999210357666;
	setAttr ".tcf" 0;
	setAttr ".trsd" 1;
	setAttr ".fakc" 0;
	setAttr ".sc" -type "float3" 0.43434039 0.099828236 0.15937491 ;
	setAttr ".cp" 2.3299999237060547;
createNode ramp -n "paintfx_archives:ramp21";
	rename -uid "B6230A0C-4182-53EB-90E2-D6B1AEA0F568";
	setAttr -s 2 ".cel";
	setAttr ".cel[0].ep" 0;
	setAttr ".cel[0].ec" -type "float3" 0.81568629 0.17254902 0.14117648 ;
	setAttr ".cel[1].ep" 1;
	setAttr ".cel[1].ec" -type "float3" 1 0.098039217 0.098039217 ;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "6BD515FB-4F68-6F95-0E0E-D895BEFBB436";
	setAttr -s 27 ".lnk";
	setAttr -s 27 ".slnk";
select -ne :time1;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 27 ".st";
	setAttr -cb on ".an";
	setAttr -cb on ".pt";
select -ne :renderGlobalsList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
select -ne :defaultShaderList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 29 ".s";
select -ne :postProcessList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
	setAttr -s 2 ".r";
select -ne :defaultTextureList1;
	setAttr -s 25 ".tx";
select -ne :initialShadingGroup;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	setAttr ".ren" -type "string" "arnold";
	setAttr ".outf" 51;
	setAttr ".imfkey" -type "string" "exr";
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :defaultLightSet;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "paintfx_archives:downRed1Shader.oc" "paintfx_archives:downRed1ShaderSG.ss"
		;
connectAttr "paintfx_archives:downRed1MainShape.iog" "paintfx_archives:downRed1ShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:downRed1ShaderSG_materialRefShape.iog" "paintfx_archives:downRed1ShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:downRed1LeafShader.oc" "paintfx_archives:downRed1LeafShaderSG.ss"
		;
connectAttr "paintfx_archives:downRed1LeafShape.iog" "paintfx_archives:downRed1LeafShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:downRed1LeafShaderSG_materialRefShape.iog" "paintfx_archives:downRed1LeafShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:downRed1ShaderSG.msg" "paintfx_archives:materialInfo20.sg"
		;
connectAttr "paintfx_archives:downRed1Shader.msg" "paintfx_archives:materialInfo20.m"
		;
connectAttr "paintfx_archives:ramp20.msg" "paintfx_archives:materialInfo20.t" -na
		;
connectAttr "paintfx_archives:ramp20.oc" "paintfx_archives:downRed1Shader.c";
connectAttr "paintfx_archives:downRed1LeafShaderSG.msg" "paintfx_archives:materialInfo21.sg"
		;
connectAttr "paintfx_archives:downRed1LeafShader.msg" "paintfx_archives:materialInfo21.m"
		;
connectAttr "paintfx_archives:ramp21.msg" "paintfx_archives:materialInfo21.t" -na
		;
connectAttr "paintfx_archives:ramp21.oc" "paintfx_archives:downRed1LeafShader.c"
		;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "paintfx_archives:downRed1ShaderSG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "paintfx_archives:downRed1LeafShaderSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "paintfx_archives:downRed1ShaderSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "paintfx_archives:downRed1LeafShaderSG.message" ":defaultLightSet.message";
connectAttr "paintfx_archives:downRed1ShaderSG.pa" ":renderPartition.st" -na;
connectAttr "paintfx_archives:downRed1LeafShaderSG.pa" ":renderPartition.st" -na
		;
connectAttr "paintfx_archives:downRed1Shader.msg" ":defaultShaderList1.s" -na;
connectAttr "paintfx_archives:downRed1LeafShader.msg" ":defaultShaderList1.s" -na
		;
connectAttr "paintfx_archives:ramp20.msg" ":defaultTextureList1.tx" -na;
connectAttr "paintfx_archives:ramp21.msg" ":defaultTextureList1.tx" -na;
// End of DownRed1_ai.ma
