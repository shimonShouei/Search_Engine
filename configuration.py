import os


class ConfigClass:
    def __init__(self,corpusPath, outputPath,is_stemming):
        self.corpusPath = corpusPath
        self.outputPath = outputPath+'/'
        if not os.path.exists(self.outputPath):
            os.makedirs(self.outputPath)

        self.savedFileMainFolder = ''
        self.saveFilesWithStem = self.savedFileMainFolder + "/WithStem"
        self.saveFilesWithoutStem = self.savedFileMainFolder + "/WithoutStem"
        self.toStem = is_stemming

        print('Project was created successfully..')

    def get__corpusPath(self):
        return self.corpusPath
