# Xgen To Hou

解析XPD数据后找不到XGen中Guides和hair之间的对应关系，中道崩殂

![image](https://github.com/user-attachments/assets/b9a4c92e-a901-45f7-9d16-0c9293279671)

## Building
```
run build.bat
```

## Notes
1. 新建build文件夹
    ```
    mkdir build
    ```
2. 进入build
    ```
    cd build
    ```
3. 生成makefile
    ```
    # Linux 使用Unix生成
    cmake ../CMakeLists.txt -G "Unix Makefiles"
    默认是MSVC，需要强制使用GNU -G "Unix Makefiles"
    # Win 使用vs生成
    cmake ../CMakeLists.txt
    ```
4. 执行makefile
    ```
    # Linux
    # 使用GNU生成
    make

    # Win
    # 使用vs生成DeBug
    cmake --build .
    # 使用vs生成Release
    cmake --build . --config Release
    ```
5. 运行exe
    ```
    ./Release/XgenToHou.exe
    ```

代码有改动后重新make一下，再./Release/XgenToHou.exe执行程序即可

xgen文件夹在maya安装目录 D:\Program Files\Maya2022\plug-ins\xgen


## References

* [Groom Bake modifier](https://help.autodesk.com/view/MAYAUL/2022/ENU/?guid=GUID-725180FD-8B5D-4ABC-A4F4-2800E29888B3)
* [XPD File Specification](https://help.autodesk.com/view/MAYAUL/2022/ENU/?guid=GUID-43899CB9-CE0F-476E-9E94-591AE2F1F807)

## xgen那些事
```
XGen File Path Editing
https://forums.autodesk.com/t5/maya-forum/xgen-file-path-editing/td-p/7107623

Use python to update attributes in XGen
https://around-the-corner.typepad.com/adn/2015/12/use-python-to-update-attributes-in-xgen.html

xGen 为 Arnold 导出 alembic/ASS 文件
https://forums.autodesk.com/t5/maya-forum/xgen-export-alembic-ass-file-for-arnold/td-p/6973546
https://www.shangyexinzhi.com/article/4801515.html

XGen“自动更新预览”+ AnimWires 禁用网格变形
https://forums.autodesk.com/t5/maya-dynamics/xgen-quot-update-preview-automatically-quot-animwires-disables/td-p/7332883

Xgen Python disable a Modifier
https://forums.autodesk.com/t5/maya-programming/xgen-python-disable-a-modifier/td-p/7929617

Xgen: Guides to Curves with Python
https://forums.autodesk.com/t5/maya-programming/xgen-guides-to-curves-with-python/td-p/10232808

在Maya中使用Arnold在渲染场上渲染时，Xgen头发闪烁
https://www.autodesk.com.cn/support/technical/article/caas/sfdcarticles/sfdcarticles/CHS/Xgen-Hair-is-flickering-when-rendered-on-a-render-farm-with-Arnold-in-Maya.html
Xgen毛发渲染抖动可能原因
https://www.shangyexinzhi.com/article/3942036.html
```
* [使用py调用maya里xgen面板](maya-xgen.py)
