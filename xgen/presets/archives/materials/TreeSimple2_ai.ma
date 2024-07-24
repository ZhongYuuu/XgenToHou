//Maya ASCII 2017ff03 scene
//Name: TreeSimple2_ai.ma
//Last modified: Tue, Mar 15, 2016 02:33:49 PM
//Codeset: 1252
requires maya "2017ff03";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2017";
fileInfo "version" "Preview Release 64";
fileInfo "cutIdentifier" "201603150300-989850-2";
fileInfo "osv" "Microsoft Windows 7 Ultimate Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode transform -n "paintfx_archives:treeSimple2LeafShaderSG_materialRef";
	rename -uid "32DA5ED1-4149-85B3-FA0E-648ECD52ED65";
createNode mesh -n "paintfx_archives:treeSimple2LeafShaderSG_materialRefShape" -p
		 "paintfx_archives:treeSimple2LeafShaderSG_materialRef";
	rename -uid "2A730C24-435E-D5C2-F7FD-9084892F28E3";
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
createNode transform -n "paintfx_archives:treeSimple2ShaderSG_materialRef";
	rename -uid "31E91FBC-42DD-8DBC-F8F5-2F97A9E09064";
createNode mesh -n "paintfx_archives:treeSimple2ShaderSG_materialRefShape" -p "paintfx_archives:treeSimple2ShaderSG_materialRef";
	rename -uid "C6E7BDF3-4A89-A230-677F-0E8A69BA433B";
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
createNode shadingEngine -n "paintfx_archives:treeSimple2LeafShaderSG";
	rename -uid "5C2DE99A-4659-6FCA-4299-2D96209CFCC9";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
createNode shadingEngine -n "paintfx_archives:treeSimple2ShaderSG";
	rename -uid "81ACA0E2-4F57-192C-373B-76ACBA7B364B";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
createNode materialInfo -n "paintfx_archives:materialInfo16";
	rename -uid "AA036565-438E-1636-D38E-B59E4BBA6BFB";
createNode phong -n "paintfx_archives:treeSimple2LeafShader";
	rename -uid "54970841-4FFB-E2AC-DC78-17A9F8774B56";
	setAttr ".dc" 0.43902000784873962;
	setAttr ".tc" 0.56098002195358276;
	setAttr ".tcf" 0;
	setAttr ".trsd" 1;
	setAttr ".fakc" 0;
	setAttr ".sc" -type "float3" 0 0 0 ;
	setAttr ".cp" 10;
createNode ramp -n "paintfx_archives:ramp16";
	rename -uid "881DDA7B-4294-17DE-4101-04AD6A40084B";
	setAttr -s 2 ".cel";
	setAttr ".cel[0].ep" 0;
	setAttr ".cel[0].ec" -type "float3" 0.16078432 0.49411765 0.24705882 ;
	setAttr ".cel[1].ep" 1;
	setAttr ".cel[1].ec" -type "float3" 0.43529412 0.66274512 0.32549021 ;
createNode materialInfo -n "paintfx_archives:materialInfo15";
	rename -uid "EADC88F5-45E6-63A4-1828-79B140B25BD1";
createNode phong -n "paintfx_archives:treeSimple2Shader";
	rename -uid "8D39747B-448A-3E3A-5796-25A59DDBB29F";
	setAttr ".tc" 0.20000000298023224;
	setAttr ".tcf" 0;
	setAttr ".trsd" 1;
	setAttr ".fakc" 0;
	setAttr ".sc" -type "float3" 0 0 0 ;
	setAttr ".cp" 10;
createNode ramp -n "paintfx_archives:ramp15";
	rename -uid "BD6B04DC-477F-9308-3960-DEA78B0D8294";
	setAttr -s 2 ".cel";
	setAttr ".cel[0].ep" 0;
	setAttr ".cel[0].ec" -type "float3" 0 0 0 ;
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
connectAttr "paintfx_archives:treeSimple2LeafShader.oc" "paintfx_archives:treeSimple2LeafShaderSG.ss"
		;
connectAttr "paintfx_archives:treeSimple2LeafShape.iog" "paintfx_archives:treeSimple2LeafShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:treeSimple2LeafShaderSG_materialRefShape.iog" "paintfx_archives:treeSimple2LeafShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:treeSimple2Shader.oc" "paintfx_archives:treeSimple2ShaderSG.ss"
		;
connectAttr "paintfx_archives:treeSimple2MainShape.iog" "paintfx_archives:treeSimple2ShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:treeSimple2ShaderSG_materialRefShape.iog" "paintfx_archives:treeSimple2ShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:treeSimple2LeafShaderSG.msg" "paintfx_archives:materialInfo16.sg"
		;
connectAttr "paintfx_archives:treeSimple2LeafShader.msg" "paintfx_archives:materialInfo16.m"
		;
connectAttr "paintfx_archives:ramp16.msg" "paintfx_archives:materialInfo16.t" -na
		;
connectAttr "paintfx_archives:ramp16.oc" "paintfx_archives:treeSimple2LeafShader.c"
		;
connectAttr "paintfx_archives:treeSimple2ShaderSG.msg" "paintfx_archives:materialInfo15.sg"
		;
connectAttr "paintfx_archives:treeSimple2Shader.msg" "paintfx_archives:materialInfo15.m"
		;
connectAttr "paintfx_archives:ramp15.msg" "paintfx_archives:materialInfo15.t" -na
		;
connectAttr "paintfx_archives:ramp15.oc" "paintfx_archives:treeSimple2Shader.c";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "paintfx_archives:treeSimple2ShaderSG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "paintfx_archives:treeSimple2LeafShaderSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "paintfx_archives:treeSimple2ShaderSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "paintfx_archives:treeSimple2LeafShaderSG.message" ":defaultLightSet.message";
connectAttr "paintfx_archives:treeSimple2ShaderSG.pa" ":renderPartition.st" -na;
connectAttr "paintfx_archives:treeSimple2LeafShaderSG.pa" ":renderPartition.st" 
		-na;
connectAttr "paintfx_archives:treeSimple2Shader.msg" ":defaultShaderList1.s" -na
		;
connectAttr "paintfx_archives:treeSimple2LeafShader.msg" ":defaultShaderList1.s"
		 -na;
connectAttr "paintfx_archives:ramp15.msg" ":defaultTextureList1.tx" -na;
connectAttr "paintfx_archives:ramp16.msg" ":defaultTextureList1.tx" -na;
// End of TreeSimple2_ai.ma
