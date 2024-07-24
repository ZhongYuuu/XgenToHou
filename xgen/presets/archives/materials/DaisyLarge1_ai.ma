//Maya ASCII 2017ff03 scene
//Name: DaisyLarge1_ai.ma
//Last modified: Tue, Mar 15, 2016 02:25:07 PM
//Codeset: 1252
requires maya "2017ff03";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2017";
fileInfo "version" "Preview Release 64";
fileInfo "cutIdentifier" "201603150300-989850-2";
fileInfo "osv" "Microsoft Windows 7 Ultimate Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode transform -n "paintfx_archives:daisyLarge1FlowerShaderSG_materialRef";
	rename -uid "A0822A0F-4160-C635-AE08-B8AF644A58D9";
createNode mesh -n "paintfx_archives:daisyLarge1FlowerShaderSG_materialRefShape" 
		-p "paintfx_archives:daisyLarge1FlowerShaderSG_materialRef";
	rename -uid "5A5823BD-4316-99A8-AE73-23B5C24F2308";
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
createNode transform -n "paintfx_archives:daisyLarge1ShaderSG_materialRef";
	rename -uid "87262422-4D08-0ACE-AE7F-C0A3A41E2450";
createNode mesh -n "paintfx_archives:daisyLarge1ShaderSG_materialRefShape" -p "paintfx_archives:daisyLarge1ShaderSG_materialRef";
	rename -uid "E319E811-40DC-2F6D-EF69-B3BB9DB7A738";
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
createNode transform -n "paintfx_archives:daisyLarge1LeafShaderSG_materialRef";
	rename -uid "070C909E-4555-DC5A-DE3F-0895D59EA33E";
createNode mesh -n "paintfx_archives:daisyLarge1LeafShaderSG_materialRefShape" -p
		 "paintfx_archives:daisyLarge1LeafShaderSG_materialRef";
	rename -uid "50B27B00-432F-6895-84CA-F79FB3428BF7";
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
createNode shadingEngine -n "paintfx_archives:daisyLarge1FlowerShaderSG";
	rename -uid "644C4DFD-483E-759F-1A78-C8A464AF5281";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
createNode shadingEngine -n "paintfx_archives:daisyLarge1ShaderSG";
	rename -uid "CE3A803A-42D3-A04D-5126-7E990E78CF22";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
createNode shadingEngine -n "paintfx_archives:daisyLarge1LeafShaderSG";
	rename -uid "81AB23EC-40FF-0BA0-2873-7DB80AE5C2E9";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
createNode materialInfo -n "paintfx_archives:materialInfo6";
	rename -uid "E17177C1-4564-BD60-34E6-37A3416C3149";
createNode phong -n "paintfx_archives:daisyLarge1FlowerShader";
	rename -uid "4E569381-47BB-B3AD-7DFC-F3905B511C42";
	setAttr ".dc" 0.422760009765625;
	setAttr ".tc" 0.577239990234375;
	setAttr ".tcf" 0;
	setAttr ".trsd" 1;
	setAttr ".fakc" 0;
	setAttr ".sc" -type "float3" 0.15534 0.15534 0.15534 ;
	setAttr ".cp" 10.485600471496582;
createNode ramp -n "paintfx_archives:ramp6";
	rename -uid "FAEB4D4D-4606-8724-8D18-0C875DF94DCE";
	setAttr -s 2 ".cel";
	setAttr ".cel[0].ep" 0;
	setAttr ".cel[0].ec" -type "float3" 0.84313726 0.90588236 0.89411765 ;
	setAttr ".cel[1].ep" 1;
	setAttr ".cel[1].ec" -type "float3" 1 1 1 ;
createNode materialInfo -n "paintfx_archives:materialInfo4";
	rename -uid "7ACA7EE3-4246-218C-D25B-A0A6C955E853";
createNode phong -n "paintfx_archives:daisyLarge1Shader";
	rename -uid "12B6AA1D-4B6B-6957-8674-6FBA7E0C956D";
	setAttr ".dc" 0.5121999979019165;
	setAttr ".tc" 0.4878000020980835;
	setAttr ".tcf" 0;
	setAttr ".trsd" 1;
	setAttr ".fakc" 0;
	setAttr ".sc" -type "float3" 0.15534 0.15534 0.15534 ;
	setAttr ".cp" 10.485600471496582;
createNode ramp -n "paintfx_archives:ramp4";
	rename -uid "1CABB628-4E9E-F5AB-6C4B-B799312EFEE3";
	setAttr -s 2 ".cel";
	setAttr ".cel[0].ep" 0;
	setAttr ".cel[0].ec" -type "float3" 0.1435992 0.21346863 0.10968237 ;
	setAttr ".cel[1].ep" 1;
	setAttr ".cel[1].ec" -type "float3" 0.17269155 0.4627451 0.35025415 ;
createNode materialInfo -n "paintfx_archives:materialInfo5";
	rename -uid "A5A41F05-4AEC-2105-F569-C49C53B9EC8E";
createNode phong -n "paintfx_archives:daisyLarge1LeafShader";
	rename -uid "15EA60D3-4E65-4D9A-0A86-4CA99A8677A3";
	setAttr ".dc" 0.67479997873306274;
	setAttr ".tc" 0.32519999146461487;
	setAttr ".tcf" 0;
	setAttr ".trsd" 1;
	setAttr ".fakc" 0;
	setAttr ".sc" -type "float3" 0.15534 0.15534 0.15534 ;
	setAttr ".cp" 10.485600471496582;
createNode ramp -n "paintfx_archives:ramp5";
	rename -uid "E71E4EB0-4A03-3918-43C9-A6A4F1BA7A1F";
	setAttr -s 2 ".cel";
	setAttr ".cel[0].ep" 0;
	setAttr ".cel[0].ec" -type "float3" 0.062745094 0.20392157 0.098039217 ;
	setAttr ".cel[1].ep" 1;
	setAttr ".cel[1].ec" -type "float3" 0.14509805 0.21960784 0.10980392 ;
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
connectAttr "paintfx_archives:daisyLarge1FlowerShader.oc" "paintfx_archives:daisyLarge1FlowerShaderSG.ss"
		;
connectAttr "paintfx_archives:daisyLarge1FlowerShape.iog" "paintfx_archives:daisyLarge1FlowerShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:daisyLarge1FlowerShaderSG_materialRefShape.iog" "paintfx_archives:daisyLarge1FlowerShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:daisyLarge1Shader.oc" "paintfx_archives:daisyLarge1ShaderSG.ss"
		;
connectAttr "paintfx_archives:daisyLarge1MainShape.iog" "paintfx_archives:daisyLarge1ShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:daisyLarge1ShaderSG_materialRefShape.iog" "paintfx_archives:daisyLarge1ShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:daisyLarge1LeafShader.oc" "paintfx_archives:daisyLarge1LeafShaderSG.ss"
		;
connectAttr "paintfx_archives:daisyLarge1LeafShape.iog" "paintfx_archives:daisyLarge1LeafShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:daisyLarge1LeafShaderSG_materialRefShape.iog" "paintfx_archives:daisyLarge1LeafShaderSG.dsm"
		 -na;
connectAttr "paintfx_archives:daisyLarge1FlowerShaderSG.msg" "paintfx_archives:materialInfo6.sg"
		;
connectAttr "paintfx_archives:daisyLarge1FlowerShader.msg" "paintfx_archives:materialInfo6.m"
		;
connectAttr "paintfx_archives:ramp6.msg" "paintfx_archives:materialInfo6.t" -na;
connectAttr "paintfx_archives:ramp6.oc" "paintfx_archives:daisyLarge1FlowerShader.c"
		;
connectAttr "paintfx_archives:daisyLarge1ShaderSG.msg" "paintfx_archives:materialInfo4.sg"
		;
connectAttr "paintfx_archives:daisyLarge1Shader.msg" "paintfx_archives:materialInfo4.m"
		;
connectAttr "paintfx_archives:ramp4.msg" "paintfx_archives:materialInfo4.t" -na;
connectAttr "paintfx_archives:ramp4.oc" "paintfx_archives:daisyLarge1Shader.c";
connectAttr "paintfx_archives:daisyLarge1LeafShaderSG.msg" "paintfx_archives:materialInfo5.sg"
		;
connectAttr "paintfx_archives:daisyLarge1LeafShader.msg" "paintfx_archives:materialInfo5.m"
		;
connectAttr "paintfx_archives:ramp5.msg" "paintfx_archives:materialInfo5.t" -na;
connectAttr "paintfx_archives:ramp5.oc" "paintfx_archives:daisyLarge1LeafShader.c"
		;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "paintfx_archives:daisyLarge1ShaderSG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "paintfx_archives:daisyLarge1LeafShaderSG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "paintfx_archives:daisyLarge1FlowerShaderSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "paintfx_archives:daisyLarge1ShaderSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "paintfx_archives:daisyLarge1LeafShaderSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "paintfx_archives:daisyLarge1FlowerShaderSG.message" ":defaultLightSet.message";
connectAttr "paintfx_archives:daisyLarge1ShaderSG.pa" ":renderPartition.st" -na;
connectAttr "paintfx_archives:daisyLarge1LeafShaderSG.pa" ":renderPartition.st" 
		-na;
connectAttr "paintfx_archives:daisyLarge1FlowerShaderSG.pa" ":renderPartition.st"
		 -na;
connectAttr "paintfx_archives:daisyLarge1Shader.msg" ":defaultShaderList1.s" -na
		;
connectAttr "paintfx_archives:daisyLarge1LeafShader.msg" ":defaultShaderList1.s"
		 -na;
connectAttr "paintfx_archives:daisyLarge1FlowerShader.msg" ":defaultShaderList1.s"
		 -na;
connectAttr "paintfx_archives:ramp4.msg" ":defaultTextureList1.tx" -na;
connectAttr "paintfx_archives:ramp5.msg" ":defaultTextureList1.tx" -na;
connectAttr "paintfx_archives:ramp6.msg" ":defaultTextureList1.tx" -na;
// End of DaisyLarge1_ai.ma
