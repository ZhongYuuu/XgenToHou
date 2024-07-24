
#include <fstream>
#include <string>
#include <iostream>

#include <porting/safevector.h>
#include <xpd/src/core/Xpd.h>


int main()
{
    XpdReader* xpd;
    std::string filename = "../../samples/pSphere1.xpd";

    std::string txtFile = "output.txt";
    std::ofstream outfile(txtFile);

    xpd = XpdReader::open(filename);
    if (!xpd) {
        std::cerr << "Failed to open xuv file: " << filename << std::endl;
        return 0;
    }

    // Put out the file header
    xpd->print(std::cout);
    xpd->print(outfile);
    
    while (xpd->nextFace()) {

        // Put out the face header
        xpd->print(std::cout);
        xpd->print(outfile);

        while (xpd->nextBlock()) {

            // Put out the block name
            xpd->print(std::cout);
            xpd->print(outfile);

            safevector<float> data;
            while (xpd->readPrim(data)) {

                // Dump out the data
                std::cout << "        ";
                outfile << "        ";
                for (unsigned int i = 0; i < data.size(); i++) {
                    std::cout << data[i] << " ";
                    outfile << data[i] << " ";
                }
                std::cout << std::endl;
                outfile << std::endl;
            }
        }
    }

    xpd->close();
    outfile.close();

    std::cout << std::endl << "Success." << std::endl;
    getchar();
    return 0;
}
