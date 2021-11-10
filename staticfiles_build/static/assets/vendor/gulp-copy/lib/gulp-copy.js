const path = require('path');
const fs = require('fs');
const through = require('through2');
const PluginError = require('plugin-error');

const separator = path.sep;

/**
 * gulp copy method
 * @param {string} destination
 * @param {object} opts
 * @returns {object}
 */
function gulpCopy(destination, opts) {
    const throughOptions = { objectMode: true };

    // Make sure a destination was verified
    if (typeof destination !== 'string') {
        throw new PluginError('gulp-copy', 'No valid destination specified');
    }

    // Default options
    if (opts === undefined) {
        opts = opts || {};
    } else if (typeof opts !== 'object' || opts === null) {
        throw new PluginError('gulp-copy', 'No valid options specified');
    }

    return through(throughOptions, transform);

    /**
     * Transform method, copies the file to its new destination
     * @param {object} file
     * @param {string} encoding
     * @param {function} cb
     */
    function transform(file, encoding, cb) {
        let rel = null;
        let fileDestination = null;

        if (file.isStream()) {
            cb(new PluginError('gulp-copy', 'Streaming not supported'));
        }

        if (file.isNull()) {
            cb(null, file);
        } else {
            rel = path.relative(file.cwd, file.path).replace(/\\/g, separator);

            // Strip path prefixes
            if (opts.prefix) {
                let p = opts.prefix;
                while (p-- > 0) {
                    rel = rel.substring(rel.indexOf(separator) + 1);
                }
            }

            fileDestination = path.join(destination, rel);

            // Make sure destination exists
            if (!doesPathExist(fileDestination)) {
                createDestination(fileDestination.substr(0, fileDestination.lastIndexOf(separator)));
            }

            // Copy the file
            copyFile(file.path, fileDestination, function copyFileCallback(error) {
                if (error) {
                    throw new PluginError('gulp-copy', `Could not copy file <${file.path}>: ${error.message}`);
                }

                // Update path for file so this path is used later on
                file.path = fileDestination;
                cb(null, file);
            });
        }
    }
}

/**
 * Recursively creates the path
 * @param {string} destination
 */
function createDestination(destination) {
    const folders = destination.split(separator);
    const pathParts = [];
    const l = folders.length;

    // for absolute paths
    if (folders[0] === '') {
        pathParts.push(separator);
        folders.shift();
    }

    for (let i = 0; i < l; i++) {
        pathParts.push(folders[i]);

        if (folders[i] !== '' && !doesPathExist(pathParts.join(separator))) {
            try {
                fs.mkdirSync(pathParts.join(separator));
            } catch (error) {
                throw new PluginError('gulp-copy', `Could not create destination <${destination}>: ${error.message}`);
            }
        }
    }
}

/**
 * Check if the path exists
 * @param path
 * @returns {boolean}
 */
function doesPathExist(pathToVerify) {
    let pathExists = true;

    try {
        fs.accessSync(pathToVerify);
    } catch (error) {
        pathExists = false;
    }

    return pathExists;
}

/**
 * Copy a file to its new destination
 * @param {string} source
 * @param {string} target
 * @param {function} copyCallback
 */
function copyFile(source, target, copyCallback) {
    const readStream = fs.createReadStream(source);
    const writeStream = fs.createWriteStream(target);
    let done = false;

    readStream.on('error', copyDone);
    writeStream.on('error', copyDone);

    writeStream.on('close', function onWriteCb() {
        copyDone(null);
    });

    readStream.pipe(writeStream);

    /**
     * Finish copying. Reports error when needed
     * @param [error] optional error
     */
    function copyDone(error) {
        if (!done) {
            done = true;
            copyCallback(error);
        }
    }
}

module.exports = gulpCopy;
