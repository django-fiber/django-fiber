qq.FineUploaderBasic = function(o){
    var that = this;
    this._options = {
        debug: false,
        button: null,
        multiple: true,
        maxConnections: 3,
        disableCancelForFormUploads: false,
        autoUpload: true,
        request: {
            endpoint: '/server/upload',
            params: {},
            paramsInBody: false,
            customHeaders: {},
            forceMultipart: true,
            inputName: 'qqfile',
            uuidName: 'qquuid',
            totalFileSizeName: 'qqtotalfilesize'
        },
        validation: {
            allowedExtensions: [],
            sizeLimit: 0,
            minSizeLimit: 0,
            stopOnFirstInvalidFile: true
        },
        callbacks: {
            onSubmit: function(id, fileName){},
            onComplete: function(id, fileName, responseJSON){},
            onCancel: function(id, fileName){},
            onUpload: function(id, fileName){},
            onUploadChunk: function(id, fileName, chunkData){},
            onResume: function(id, fileName, chunkData){},
            onProgress: function(id, fileName, loaded, total){},
            onError: function(id, fileName, reason) {},
            onAutoRetry: function(id, fileName, attemptNumber) {},
            onManualRetry: function(id, fileName) {},
            onValidateBatch: function(fileData) {},
            onValidate: function(fileData) {}
        },
        messages: {
            typeError: "{file} has an invalid extension. Valid extension(s): {extensions}.",
            sizeError: "{file} is too large, maximum file size is {sizeLimit}.",
            minSizeError: "{file} is too small, minimum file size is {minSizeLimit}.",
            emptyError: "{file} is empty, please select files again without it.",
            noFilesError: "No files to upload.",
            onLeave: "The files are being uploaded, if you leave now the upload will be cancelled."
        },
        retry: {
            enableAuto: false,
            maxAutoAttempts: 3,
            autoAttemptDelay: 5,
            preventRetryResponseProperty: 'preventRetry'
        },
        classes: {
            buttonHover: 'qq-upload-button-hover',
            buttonFocus: 'qq-upload-button-focus'
        },
        chunking: {
            enabled: false,
            partSize: 2000000,
            paramNames: {
                partIndex: 'qqpartindex',
                partByteOffset: 'qqpartbyteoffset',
                chunkSize: 'qqchunksize',
                totalFileSize: 'qqtotalfilesize',
                totalParts: 'qqtotalparts',
                filename: 'qqfilename'
            }
        },
        resume: {
            enabled: false,
            id: null,
            cookiesExpireIn: 7, //days
            paramNames: {
                resuming: "qqresume"
            }
        },
        formatFileName: function(fileName) {
            if (fileName.length > 33) {
                fileName = fileName.slice(0, 19) + '...' + fileName.slice(-14);
            }
            return fileName;
        },
        text: {
            sizeSymbols: ['kB', 'MB', 'GB', 'TB', 'PB', 'EB']
        }
    };

    qq.extend(this._options, o, true);
    this._wrapCallbacks();
    this._disposeSupport =  new qq.DisposeSupport();

    // number of files being uploaded
    this._filesInProgress = [];

    this._storedFileIds = [];

    this._autoRetries = [];
    this._retryTimeouts = [];
    this._preventRetries = [];

    this._paramsStore = this._createParamsStore();
    this._endpointStore = this._createEndpointStore();

    this._handler = this._createUploadHandler();

    if (this._options.button){
        this._button = this._createUploadButton(this._options.button);
    }

    this._preventLeaveInProgress();
};

qq.FineUploaderBasic.prototype = {
    log: function(str, level) {
        if (this._options.debug && (!level || level === 'info')) {
            qq.log('[FineUploader] ' + str);
        }
        else if (level && level !== 'info') {
            qq.log('[FineUploader] ' + str, level);

        }
    },
    setParams: function(params, fileId) {
        /*jshint eqeqeq: true, eqnull: true*/
        if (fileId == null) {
            this._options.request.params = params;
        }
        else {
            this._paramsStore.setParams(params, fileId);
        }
    },
    setEndpoint: function(endpoint, fileId) {
        /*jshint eqeqeq: true, eqnull: true*/
        if (fileId == null) {
            this._options.request.endpoint = endpoint;
        }
        else {
            this._endpointStore.setEndpoint(endpoint, fileId);
        }
    },
    getInProgress: function(){
        return this._filesInProgress.length;
    },
    uploadStoredFiles: function(){
        "use strict";
        var idToUpload;

        while(this._storedFileIds.length) {
            idToUpload = this._storedFileIds.shift();
            this._filesInProgress.push(idToUpload);
            this._handler.upload(idToUpload);
        }
    },
    clearStoredFiles: function(){
        this._storedFileIds = [];
    },
    retry: function(id) {
        if (this._onBeforeManualRetry(id)) {
            this._handler.retry(id);
            return true;
        }
        else {
            return false;
        }
    },
    cancel: function(fileId) {
        this._handler.cancel(fileId);
    },
    reset: function() {
        this.log("Resetting uploader...");
        this._handler.reset();
        this._filesInProgress = [];
        this._storedFileIds = [];
        this._autoRetries = [];
        this._retryTimeouts = [];
        this._preventRetries = [];
        this._button.reset();
        this._paramsStore.reset();
        this._endpointStore.reset();
    },
    addFiles: function(filesOrInputs) {
        var self = this,
            verifiedFilesOrInputs = [],
            index, fileOrInput;

        if (filesOrInputs) {
            if (!window.FileList || !(filesOrInputs instanceof FileList)) {
                filesOrInputs = [].concat(filesOrInputs);
            }

            for (index = 0; index < filesOrInputs.length; index+=1) {
                fileOrInput = filesOrInputs[index];

                if (qq.isFileOrInput(fileOrInput)) {
                    verifiedFilesOrInputs.push(fileOrInput);
                }
                else {
                    self.log(fileOrInput + ' is not a File or INPUT element!  Ignoring!', 'warn');
                }
            }

            this.log('Processing ' + verifiedFilesOrInputs.length + ' files or inputs...');
            this._uploadFileList(verifiedFilesOrInputs);
        }
    },
    getUuid: function(fileId) {
        return this._handler.getUuid(fileId);
    },
    getResumableFilesData: function() {
        return this._handler.getResumableFilesData();
    },
    getSize: function(fileId) {
        return this._handler.getSize(fileId);
    },
    getFile: function(fileId) {
        return this._handler.getFile(fileId);
    },
    _createUploadButton: function(element){
        var self = this;

        var button = new qq.UploadButton({
            element: element,
            multiple: this._options.multiple && qq.isXhrUploadSupported(),
            acceptFiles: this._options.validation.acceptFiles,
            onChange: function(input){
                self._onInputChange(input);
            },
            hoverClass: this._options.classes.buttonHover,
            focusClass: this._options.classes.buttonFocus
        });

        this._disposeSupport.addDisposer(function() { button.dispose(); });
        return button;
    },
    _createUploadHandler: function(){
        var self = this;

        return new qq.UploadHandler({
            debug: this._options.debug,
            forceMultipart: this._options.request.forceMultipart,
            maxConnections: this._options.maxConnections,
            customHeaders: this._options.request.customHeaders,
            customFields: this._options.request.customFields,
            inputName: this._options.request.inputName,
            uuidParamName: this._options.request.uuidName,
            totalFileSizeParamName: this._options.request.totalFileSizeName,
            demoMode: this._options.demoMode,
            paramsInBody: this._options.request.paramsInBody,
            paramsStore: this._paramsStore,
            endpointStore: this._endpointStore,
            chunking: this._options.chunking,
            resume: this._options.resume,
            log: function(str, level) {
                self.log(str, level);
            },
            onProgress: function(id, fileName, loaded, total){
                self._onProgress(id, fileName, loaded, total);
                self._options.callbacks.onProgress(id, fileName, loaded, total);
            },
            onComplete: function(id, fileName, result, xhr){
                self._onComplete(id, fileName, result, xhr);
                self._options.callbacks.onComplete(id, fileName, result);
            },
            onCancel: function(id, fileName){
                self._onCancel(id, fileName);
                self._options.callbacks.onCancel(id, fileName);
            },
            onUpload: function(id, fileName){
                self._onUpload(id, fileName);
                self._options.callbacks.onUpload(id, fileName);
            },
            onUploadChunk: function(id, fileName, chunkData){
                self._options.callbacks.onUploadChunk(id, fileName, chunkData);
            },
            onResume: function(id, fileName, chunkData) {
                return self._options.callbacks.onResume(id, fileName, chunkData);
            },
            onAutoRetry: function(id, fileName, responseJSON, xhr) {
                self._preventRetries[id] = responseJSON[self._options.retry.preventRetryResponseProperty];

                if (self._shouldAutoRetry(id, fileName, responseJSON)) {
                    self._maybeParseAndSendUploadError(id, fileName, responseJSON, xhr);
                    self._options.callbacks.onAutoRetry(id, fileName, self._autoRetries[id] + 1);
                    self._onBeforeAutoRetry(id, fileName);

                    self._retryTimeouts[id] = setTimeout(function() {
                        self._onAutoRetry(id, fileName, responseJSON)
                    }, self._options.retry.autoAttemptDelay * 1000);

                    return true;
                }
                else {
                    return false;
                }
            }
        });
    },
    _preventLeaveInProgress: function(){
        var self = this;

        this._disposeSupport.attach(window, 'beforeunload', function(e){
            if (!self._filesInProgress.length){return;}

            var e = e || window.event;
            // for ie, ff
            e.returnValue = self._options.messages.onLeave;
            // for webkit
            return self._options.messages.onLeave;
        });
    },
    _onSubmit: function(id, fileName){
        if (this._options.autoUpload) {
            this._filesInProgress.push(id);
        }
    },
    _onProgress: function(id, fileName, loaded, total){
    },
    _onComplete: function(id, fileName, result, xhr){
        this._removeFromFilesInProgress(id);
        this._maybeParseAndSendUploadError(id, fileName, result, xhr);
    },
    _onCancel: function(id, fileName){
        this._removeFromFilesInProgress(id);

        clearTimeout(this._retryTimeouts[id]);

        var storedFileIndex = qq.indexOf(this._storedFileIds, id);
        if (!this._options.autoUpload && storedFileIndex >= 0) {
            this._storedFileIds.splice(storedFileIndex, 1);
        }
    },
    _removeFromFilesInProgress: function(id) {
        var index = qq.indexOf(this._filesInProgress, id);
        if (index >= 0) {
            this._filesInProgress.splice(index, 1);
        }
    },
    _onUpload: function(id, fileName){},
    _onInputChange: function(input){
        if (qq.isXhrUploadSupported()){
            this.addFiles(input.files);
        } else {
            this.addFiles(input);
        }
        this._button.reset();
    },
    _onBeforeAutoRetry: function(id, fileName) {
        this.log("Waiting " + this._options.retry.autoAttemptDelay + " seconds before retrying " + fileName + "...");
    },
    _onAutoRetry: function(id, fileName, responseJSON) {
        this.log("Retrying " + fileName + "...");
        this._autoRetries[id]++;
        this._handler.retry(id);
    },
    _shouldAutoRetry: function(id, fileName, responseJSON) {
        if (!this._preventRetries[id] && this._options.retry.enableAuto) {
            if (this._autoRetries[id] === undefined) {
                this._autoRetries[id] = 0;
            }

            return this._autoRetries[id] < this._options.retry.maxAutoAttempts
        }

        return false;
    },
    //return false if we should not attempt the requested retry
    _onBeforeManualRetry: function(id) {
        if (this._preventRetries[id]) {
            this.log("Retries are forbidden for id " + id, 'warn');
            return false;
        }
        else if (this._handler.isValid(id)) {
            var fileName = this._handler.getName(id);

            if (this._options.callbacks.onManualRetry(id, fileName) === false) {
                return false;
            }

            this.log("Retrying upload for '" + fileName + "' (id: " + id + ")...");
            this._filesInProgress.push(id);
            return true;
        }
        else {
            this.log("'" + id + "' is not a valid file ID", 'error');
            return false;
        }
    },
    _maybeParseAndSendUploadError: function(id, fileName, response, xhr) {
        //assuming no one will actually set the response code to something other than 200 and still set 'success' to true
        if (!response.success){
            if (xhr && xhr.status !== 200 && !response.error) {
                this._options.callbacks.onError(id, fileName, "XHR returned response code " + xhr.status);
            }
            else {
                var errorReason = response.error ? response.error : "Upload failure reason unknown";
                this._options.callbacks.onError(id, fileName, errorReason);
            }
        }
    },
    _uploadFileList: function(files){
        var validationDescriptors, index, batchInvalid;

        validationDescriptors = this._getValidationDescriptors(files);
        batchInvalid = this._options.callbacks.onValidateBatch(validationDescriptors) === false;

        if (!batchInvalid) {
            if (files.length > 0) {
                for (index = 0; index < files.length; index++){
                    if (this._validateFile(files[index])){
                        this._uploadFile(files[index]);
                    } else {
                        if (this._options.validation.stopOnFirstInvalidFile){
                            return;
                        }
                    }
                }
            }
            else {
                this._error('noFilesError', "");
            }
        }
    },
    _uploadFile: function(fileContainer){
        var id = this._handler.add(fileContainer);
        var fileName = this._handler.getName(id);

        if (this._options.callbacks.onSubmit(id, fileName) !== false){
            this._onSubmit(id, fileName);
            if (this._options.autoUpload) {
                this._handler.upload(id);
            }
            else {
                this._storeFileForLater(id);
            }
        }
    },
    _storeFileForLater: function(id) {
        this._storedFileIds.push(id);
    },
    _validateFile: function(file){
        var validationDescriptor, name, size;

        validationDescriptor = this._getValidationDescriptor(file);
        name = validationDescriptor.name;
        size = validationDescriptor.size;

        if (this._options.callbacks.onValidate(validationDescriptor) === false) {
            return false;
        }

        if (!this._isAllowedExtension(name)){
            this._error('typeError', name);
            return false;

        }
        else if (size === 0){
            this._error('emptyError', name);
            return false;

        }
        else if (size && this._options.validation.sizeLimit && size > this._options.validation.sizeLimit){
            this._error('sizeError', name);
            return false;

        }
        else if (size && size < this._options.validation.minSizeLimit){
            this._error('minSizeError', name);
            return false;
        }

        return true;
    },
    _error: function(code, fileName){
        var message = this._options.messages[code];
        function r(name, replacement){ message = message.replace(name, replacement); }

        var extensions = this._options.validation.allowedExtensions.join(', ').toLowerCase();

        r('{file}', this._options.formatFileName(fileName));
        r('{extensions}', extensions);
        r('{sizeLimit}', this._formatSize(this._options.validation.sizeLimit));
        r('{minSizeLimit}', this._formatSize(this._options.validation.minSizeLimit));

        this._options.callbacks.onError(null, fileName, message);

        return message;
    },
    _isAllowedExtension: function(fileName){
        var allowed = this._options.validation.allowedExtensions,
            valid = false;

        if (!allowed.length) {
            return true;
        }

        qq.each(allowed, function(idx, allowedExt) {
            /*jshint eqeqeq: true, eqnull: true*/
            var extRegex = new RegExp('\\.' + allowedExt + "$", 'i');

            if (fileName.match(extRegex) != null) {
                valid = true;
                return false;
            }
        });

        return valid;
    },
    _formatSize: function(bytes){
        var i = -1;
        do {
            bytes = bytes / 1024;
            i++;
        } while (bytes > 99);

        return Math.max(bytes, 0.1).toFixed(1) + this._options.text.sizeSymbols[i];
    },
    _wrapCallbacks: function() {
        var self, safeCallback;

        self = this;

        safeCallback = function(name, callback, args) {
            try {
                return callback.apply(self, args);
            }
            catch (exception) {
                self.log("Caught exception in '" + name + "' callback - " + exception.message, 'error');
            }
        }

        for (var prop in this._options.callbacks) {
            (function() {
                var callbackName, callbackFunc;
                callbackName = prop;
                callbackFunc = self._options.callbacks[callbackName];
                self._options.callbacks[callbackName] = function() {
                    return safeCallback(callbackName, callbackFunc, arguments);
                }
            }());
        }
    },
    _parseFileName: function(file) {
        var name;

        if (file.value){
            // it is a file input
            // get input value and remove path to normalize
            name = file.value.replace(/.*(\/|\\)/, "");
        } else {
            // fix missing properties in Safari 4 and firefox 11.0a2
            name = (file.fileName !== null && file.fileName !== undefined) ? file.fileName : file.name;
        }

        return name;
    },
    _parseFileSize: function(file) {
        var size;

        if (!file.value){
            // fix missing properties in Safari 4 and firefox 11.0a2
            size = (file.fileSize !== null && file.fileSize !== undefined) ? file.fileSize : file.size;
        }

        return size;
    },
    _getValidationDescriptor: function(file) {
        var name, size, fileDescriptor;

        fileDescriptor = {};
        name = this._parseFileName(file);
        size = this._parseFileSize(file);

        fileDescriptor.name = name;
        if (size) {
            fileDescriptor.size = size;
        }

        return fileDescriptor;
    },
    _getValidationDescriptors: function(files) {
        var self = this,
            fileDescriptors = [];

        qq.each(files, function(idx, file) {
            fileDescriptors.push(self._getValidationDescriptor(file));
        });

        return fileDescriptors;
    },
    _createParamsStore: function() {
        var paramsStore = {},
            self = this;

        return {
            setParams: function(params, fileId) {
                var paramsCopy = {};
                qq.extend(paramsCopy, params);
                paramsStore[fileId] = paramsCopy;
            },

            getParams: function(fileId) {
                /*jshint eqeqeq: true, eqnull: true*/
                var paramsCopy = {};

                if (fileId != null && paramsStore[fileId]) {
                    qq.extend(paramsCopy, paramsStore[fileId]);
                }
                else {
                    qq.extend(paramsCopy, self._options.request.params);
                }

                return paramsCopy;
            },

            remove: function(fileId) {
                return delete paramsStore[fileId];
            },

            reset: function() {
                paramsStore = {};
            }
        };
    },
    _createEndpointStore: function() {
        var endpointStore = {},
        self = this;

        return {
            setEndpoint: function(endpoint, fileId) {
                endpointStore[fileId] = endpoint;
            },

            getEndpoint: function(fileId) {
                /*jshint eqeqeq: true, eqnull: true*/
                if (fileId != null && endpointStore[fileId]) {
                    return endpointStore[fileId];
                }

                return self._options.request.endpoint;
            },

            remove: function(fileId) {
                return delete endpointStore[fileId];
            },

            reset: function() {
                endpointStore = {};
            }
        };
    }
};
