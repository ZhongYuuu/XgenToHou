//Maya ASCII 2017ff03 scene
//Name: TreeSimple1_ai.ma
//Last modified: Tue, Mar 15, 2016 02:32:58 PM
//Codeset: 1252
requires maya "2017ff03";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2017";
fileInfo "version" "Preview Release 64";
fileInfo "cutIdentifier" "201603150300-989850-2";
fileInfo "osv" "Microsoft Windows 7 Ultimate Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode transform -n "paintfx_archives:treeSimple1ShaderSG_materialRef";
	rename -uid "F86A67B7-444F-38FD-7DAB-C18A9A8E1696";
createNode mesh -n "paintfx_archives:treeSimple1ShaderSG_materialRefShape" -p "paintfx_archives:treeSimple1ShaderSG_materialRef";
	rename -uid "C6A5F585-44B8-F53D-1575-6F9EDB47386B";
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
createNode transform -n "paintfx_archives:treeSimple1LeafShaderSG_materialRef";
	rename -uid "F32C50C5-4644-F80D-52A8-2AA01F9870D0";
createNode mesh -n "paintfx_archives:treeSimple1LeafShaderSG_materialRefShape" -p
		 "paintfx_archives:treeSimple1LeafShaderSG_materialRef";
	rename -uid "E839F28F-4A20-6992-9592-99A183E3AC65";
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
createNode shadingEngine -n "paintfx_archives:treeSimple1ShaderSG";
	rename -uid "C57ADC0F-4DE0-75DD-19AC-25B681EB9F51";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
createNode shadingEngine -n "paintfx_archives:treeSimple1LeafShaderSG";
	rename -uid "4AC9B2F0-4C7D-45C5-94D9-B3AE3C92C4BA";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
createNode materialInfo -n "paintfx_archives:materialInfo13";
	rename -uid "21873F36-46AB-4131-9893-DBBEBA97DCF6";
createNode phong -n "paintfx_archives:treeSimple1Shader";
	rename -uid "863B4080-455D-B09D-643F-399D6C521644";
	setAttr ".tc" 0.20000000298023224;
	setAttr ".tcf" 0;
	setAttr ".trsd" 1;
	setAttr ".fakc" 0;
	setAttr ".sc" -type "float3" 0 0 0 ;
	setAttr ".cp" 10;
createNode ramp -n "paintfx_archives:ramp13";
	rename -uid "8F230516-4912-5785-3519-80A36BEEC0DB";
	setAttr -s 2 ".cel";
	setAttr ".cel[0].ep" 0;
	setAttr ".cel[0].ec" -type "float3" 0 0 0 ;
	setAttr ".cel[1].ep" 1;
	setAttr ".cel[1].ec" -type "float3" 1 1 1 ;
createNode materialInfo -n "paintfx_archives:materialInfo14";
	rename -uid "A28ED691-44F6-A753-3D7D-988CFAE7BD9B";
createNode phong -n "paintfx_archives:treeSimple1LeafShader";
	rename -uid "F3CAF9D4-414D-B3C0-5B8D-F98FBBC936D0";
	setAttr ".dc" 0.43902000784873962;
	setAttr ".tc" 0.56098002195358276;
	setAttr ".tcf" 0;
	setAttr ".trsd" 1;
	setAttr ".fakc" 0;
	setAttr ".sc" -type "float3" 0 0 0 ;
	setAttr ".cp" 10;
createNode ramp -n "paintfx_archives:ramp14";
	rename -uid "214B78B4-4A0A-FA1A-9FA6-6CB7613F6F05";
	setAttr -s 2 ".cel";
	setAttr ".cel[0].ep" 0;
	setAttr ".cel[0].ec" -type "float3" 0.16078432 0.49411765 0.24705882 ;
	setAttr ".cel[1].ep" 1;
	setAttr ".cel[1].ec" -type "float3" 0.43529412 0.66274512 0.32549021 ;
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
connectAttr "paintfx_archives:treeSimple1Shader.oc" "paintfx_archives:treeSimple1ShaderSG.ss"
		;
connectAttr "paintfx_archives:treeSimple1MainShape.iog" "paintfx_archives:treeSimple1ShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:treeSimple1ShaderSG_materialRefShape.iog" "paintfx_archives:treeSimple1ShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:treeSimple1LeafShader.oc" "paintfx_archives:treeSimple1LeafShaderSG.ss"
		;
connectAttr "paintfx_archives:treeSimple1LeafShape.iog" "paintfx_archives:treeSimple1LeafShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:treeSimple1LeafShaderSG_materialRefShape.iog" "paintfx_archives:treeSimple1LeafShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:treeSimple1ShaderSG.msg" "paintfx_archives:materialInfo13.sg"
		;
connectAttr "paintfx_archives:treeSimple1Shader.msg" "paintfx_archives:materialInfo13.m"
		;
connectAttr "paintfx_archives:ramp13.msg" "paintfx_archives:materialInfo13.t" -na
		;
connectAttr "paintfx_archives:ramp13.oc" "paintfx_archives:treeSimple1Shader.c";
connectAttr "paintfx_archives:treeSimple1LeafShaderSG.msg" "paintfx_archives:materialInfo14.sg"
		;
connectAttr "paintfx_archives:treeSimple1LeafShader.msg" "paintfx_archives:materialInfo14.m"
		;
connectAttr "paintfx_archives:ramp14.msg" "paintfx_archives:materialInfo14.t" -na
		;
connectAttr "paintfx_archives:ramp14.oc" "paintfx_archives:treeSimple1LeafShader.c"
		;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "paintfx_archives:treeSimple1ShaderSG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "paintfx_archives:treeSimple1LeafShaderSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "paintfx_archives:treeSimple1ShaderSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "paintfx_archives:treeSimple1LeafShaderSG.message" ":defaultLightSet.message";
connectAttr "paintfx_archives:treeSimple1ShaderSG.pa" ":renderPartition.st" -na;
connectAttr "paintfx_archives:treeSimple1LeafShaderSG.pa" ":renderPartition.st" 
		-na;
connectAttr "paintfx_archives:treeSimple1Shader.msg" ":defaultShaderList1.s" -na
		;
connectAttr "paintfx_archives:treeSimple1LeafShader.msg" ":defaultShaderList1.s"
		 -na;
connectAttr "paintfx_archives:ramp13.msg" ":defaultTextureList1.tx" -na;
connectAttr "paintfx_archives:ramp14.msg" ":defaultTextureList1.tx" -na;
// End of TreeSimple1_ai.ma
