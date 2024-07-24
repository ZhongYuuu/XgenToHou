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
