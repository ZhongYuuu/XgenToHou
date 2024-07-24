//Maya ASCII 2017ff03 scene
//Name: DaisyLarge2_ai.ma
//Last modified: Tue, Mar 15, 2016 02:26:21 PM
//Codeset: 1252
requires maya "2017ff03";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2017";
fileInfo "version" "Preview Release 64";
fileInfo "cutIdentifier" "201603150300-989850-2";
fileInfo "osv" "Microsoft Windows 7 Ultimate Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode transform -n "paintfx_archives:daisyLarge2ShaderSG_materialRef";
	rename -uid "6718281E-4A59-636F-245A-648A8A8F30C7";
createNode mesh -n "paintfx_archives:daisyLarge2ShaderSG_materialRefShape" -p "paintfx_archives:daisyLarge2ShaderSG_materialRef";
	rename -uid "A0B3FBCB-4F01-2A13-5620-71A74E0E4F3A";
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
createNode transform -n "paintfx_archives:daisyLarge2LeafShaderSG_materialRef";
	rename -uid "15BC987A-4884-F1A2-B8C7-11B5D9A15F0E";
createNode mesh -n "paintfx_archives:daisyLarge2LeafShaderSG_materialRefShape" -p
		 "paintfx_archives:daisyLarge2LeafShaderSG_materialRef";
	rename -uid "BAE2CECF-4C0F-CF21-134D-C194626666DC";
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
createNode transform -n "paintfx_archives:daisyLarge2FlowerShaderSG_materialRef";
	rename -uid "7CDFD328-4784-D16D-4990-3D8B250837AA";
createNode mesh -n "paintfx_archives:daisyLarge2FlowerShaderSG_materialRefShape" 
		-p "paintfx_archives:daisyLarge2FlowerShaderSG_materialRef";
	rename -uid "1376DC23-44CF-6415-B6C7-3181766EF66F";
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
createNode shadingEngine -n "paintfx_archives:daisyLarge2ShaderSG";
	rename -uid "5FE3CDE3-4C9E-ECE7-30D2-B5B6E0176BC6";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
createNode shadingEngine -n "paintfx_archives:daisyLarge2LeafShaderSG";
	rename -uid "2D7A8DAE-4240-1FD6-EFF3-8BBD8FF3823A";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
createNode shadingEngine -n "paintfx_archives:daisyLarge2FlowerShaderSG";
	rename -uid "877573CF-48AC-191D-5B04-278AA53AF91C";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
createNode materialInfo -n "paintfx_archives:materialInfo7";
	rename -uid "B1A9DEE1-4CB4-069E-74CA-07A055B3EDDF";
createNode phong -n "paintfx_archives:daisyLarge2Shader";
	rename -uid "3BC4B346-45CC-B623-7949-5394195FE713";
	setAttr ".dc" 0.5121999979019165;
	setAttr ".tc" 0.4878000020980835;
	setAttr ".tcf" 0;
	setAttr ".trsd" 1;
	setAttr ".fakc" 0;
	setAttr ".sc" -type "float3" 0.15534 0.15534 0.15534 ;
	setAttr ".cp" 10.485600471496582;
createNode ramp -n "paintfx_archives:ramp7";
	rename -uid "A520FDDD-405F-A313-2466-36A1FA7E19B5";
	setAttr -s 2 ".cel";
	setAttr ".cel[0].ep" 0;
	setAttr ".cel[0].ec" -type "float3" 0.1435992 0.21346863 0.10968237 ;
	setAttr ".cel[1].ep" 1;
	setAttr ".cel[1].ec" -type "float3" 0.17269155 0.4627451 0.35025415 ;
createNode materialInfo -n "paintfx_archives:materialInfo8";
	rename -uid "DFD6AB72-48BF-DE4C-B3A7-BF802C099B7B";
createNode phong -n "paintfx_archives:daisyLarge2LeafShader";
	rename -uid "E57521DA-41BD-EB4D-DA14-998F0BBC80AB";
	setAttr ".dc" 0.67479997873306274;
	setAttr ".tc" 0.32519999146461487;
	setAttr ".tcf" 0;
	setAttr ".trsd" 1;
	setAttr ".fakc" 0;
	setAttr ".sc" -type "float3" 0.15534 0.15534 0.15534 ;
	setAttr ".cp" 10.485600471496582;
createNode ramp -n "paintfx_archives:ramp8";
	rename -uid "AC96E5B1-4CD8-305A-68D7-7D9D00339AAE";
	setAttr -s 2 ".cel";
	setAttr ".cel[0].ep" 0;
	setAttr ".cel[0].ec" -type "float3" 0.062745094 0.20392157 0.098039217 ;
	setAttr ".cel[1].ep" 1;
	setAttr ".cel[1].ec" -type "float3" 0.14509805 0.21960784 0.10980392 ;
createNode materialInfo -n "paintfx_archives:materialInfo9";
	rename -uid "2CCDF73D-405A-6581-E444-F2AD72632F49";
createNode phong -n "paintfx_archives:daisyLarge2FlowerShader";
	rename -uid "4E078A1F-4F22-FC9B-B95F-3AA7AE27A1E7";
	setAttr ".dc" 0.422760009765625;
	setAttr ".tc" 0.577239990234375;
	setAttr ".tcf" 0;
	setAttr ".trsd" 1;
	setAttr ".fakc" 0;
	setAttr ".sc" -type "float3" 0.15534 0.15534 0.15534 ;
	setAttr ".cp" 10.485600471496582;
createNode ramp -n "paintfx_archives:ramp9";
	rename -uid "23B9597A-4FC1-A129-69E2-79A8B49465F1";
	setAttr -s 2 ".cel";
	setAttr ".cel[0].ep" 0;
	setAttr ".cel[0].ec" -type "float3" 0.84313726 0.90588236 0.89411765 ;
	setAttr ".cel[1].ep" 1;
	setAttr ".cel[1].ec" -type "float3" 1 1 1 ;
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
connectAttr "paintfx_archives:daisyLarge2Shader.oc" "paintfx_archives:daisyLarge2ShaderSG.ss"
		;
connectAttr "paintfx_archives:daisyLarge2MainShape.iog" "paintfx_archives:daisyLarge2ShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:daisyLarge2ShaderSG_materialRefShape.iog" "paintfx_archives:daisyLarge2ShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:daisyLarge2LeafShader.oc" "paintfx_archives:daisyLarge2LeafShaderSG.ss"
		;
connectAttr "paintfx_archives:daisyLarge2LeafShape.iog" "paintfx_archives:daisyLarge2LeafShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:daisyLarge2LeafShaderSG_materialRefShape.iog" "paintfx_archives:daisyLarge2LeafShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:daisyLarge2FlowerShader.oc" "paintfx_archives:daisyLarge2FlowerShaderSG.ss"
		;
connectAttr "paintfx_archives:daisyLarge2FlowerShape.iog" "paintfx_archives:daisyLarge2FlowerShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:daisyLarge2FlowerShaderSG_materialRefShape.iog" "paintfx_archives:daisyLarge2FlowerShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:daisyLarge2ShaderSG.msg" "paintfx_archives:materialInfo7.sg"
		;
connectAttr "paintfx_archives:daisyLarge2Shader.msg" "paintfx_archives:materialInfo7.m"
		;
connectAttr "paintfx_archives:ramp7.msg" "paintfx_archives:materialInfo7.t" -na;
connectAttr "paintfx_archives:ramp7.oc" "paintfx_archives:daisyLarge2Shader.c";
connectAttr "paintfx_archives:daisyLarge2LeafShaderSG.msg" "paintfx_archives:materialInfo8.sg"
		;
connectAttr "paintfx_archives:daisyLarge2LeafShader.msg" "paintfx_archives:materialInfo8.m"
		;
connectAttr "paintfx_archives:ramp8.msg" "paintfx_archives:materialInfo8.t" -na;
connectAttr "paintfx_archives:ramp8.oc" "paintfx_archives:daisyLarge2LeafShader.c"
		;
connectAttr "paintfx_archives:daisyLarge2FlowerShaderSG.msg" "paintfx_archives:materialInfo9.sg"
		;
connectAttr "paintfx_archives:daisyLarge2FlowerShader.msg" "paintfx_archives:materialInfo9.m"
		;
connectAttr "paintfx_archives:ramp9.msg" "paintfx_archives:materialInfo9.t" -na;
connectAttr "paintfx_archives:ramp9.oc" "paintfx_archives:daisyLarge2FlowerShader.c"
		;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "paintfx_archives:daisyLarge2ShaderSG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "paintfx_archives:daisyLarge2LeafShaderSG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "paintfx_archives:daisyLarge2FlowerShaderSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "paintfx_archives:daisyLarge2ShaderSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "paintfx_archives:daisyLarge2LeafShaderSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "paintfx_archives:daisyLarge2FlowerShaderSG.message" ":defaultLightSet.message";
connectAttr "paintfx_archives:daisyLarge2ShaderSG.pa" ":renderPartition.st" -na;
connectAttr "paintfx_archives:daisyLarge2LeafShaderSG.pa" ":renderPartition.st" 
		-na;
connectAttr "paintfx_archives:daisyLarge2FlowerShaderSG.pa" ":renderPartition.st"
		 -na;
connectAttr "paintfx_archives:daisyLarge2Shader.msg" ":defaultShaderList1.s" -na
		;
connectAttr "paintfx_archives:daisyLarge2LeafShader.msg" ":defaultShaderList1.s"
		 -na;
connectAttr "paintfx_archives:daisyLarge2FlowerShader.msg" ":defaultShaderList1.s"
		 -na;
connectAttr "paintfx_archives:ramp7.msg" ":defaultTextureList1.tx" -na;
connectAttr "paintfx_archives:ramp8.msg" ":defaultTextureList1.tx" -na;
connectAttr "paintfx_archives:ramp9.msg" ":defaultTextureList1.tx" -na;
// End of DaisyLarge2_ai.ma
