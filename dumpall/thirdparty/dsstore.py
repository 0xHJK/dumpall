import struct


class ParsingError(Exception):
    pass


class DataBlock(object):
    """
    Class for a basic DataBlock inside of the DS_Store format.
    """

    def __init__(self, data, debug=False):
        super(DataBlock, self).__init__()
        self.data = data
        self.pos = 0
        self.debug = debug

    def offset_read(self, length, offset=None):
        """
        Returns an byte array of length from data at the given offset or pos.
        If no offset is given, pos will be increased by length.
        Throws ParsingError if offset+length > len(self.data)
        """
        if not offset:
            offset_position = self.pos
        else:
            offset_position = offset

        if len(self.data) < offset_position + length:
            raise ParsingError("Offset+Length > len(self.data)")

        if not offset:
            self.pos += length

        value = self.data[offset_position : offset_position + length]
        self._log(
            "Reading: {}-{} => {}".format(
                hex(offset_position), hex(offset_position + length), value
            )
        )
        return value

    def skip(self, length):
        """
        Increases pos by length without reading data!
        """
        self.pos += length

    def read_filename(self):
        """
        Extracts a file name from the current position.
        """
        # The length of the file name in bytes.
        length, = struct.unpack_from(">I", self.offset_read(4))
        # The file name in UTF-16, which is two bytes per character.
        filename = self.offset_read(2 * length).decode("utf-16be")
        # A structure ID that I haven't found any use of.
        structure_id, = struct.unpack_from(">I", self.offset_read(4))
        # Now read the structure type as a string of four characters and decode it to ascii.
        structure_type, = struct.unpack_from(">4s", self.offset_read(4))

        structure_type = structure_type.decode()
        self._log("Structure type ", structure_type)
        # If we don't find a match, skip stays < 0 and we will do some magic to find the right skip due to somehow broken .DS_Store files..
        skip = -1
        # Source: http://search.cpan.org/~wiml/Mac-Finder-DSStore/DSStoreFormat.pod
        while skip < 0:
            if structure_type == "bool":
                skip = 1
            elif (
                structure_type == "type"
                or structure_type == "long"
                or structure_type == "shor"
                or structure_type == "fwsw"
                or structure_type == "fwvh"
                or structure_type == "icvt"
                or structure_type == "lsvt"
                or structure_type == "vSrn"
                or structure_type == "vstl"
            ):
                skip = 4
            elif (
                structure_type == "comp"
                or structure_type == "dutc"
                or structure_type == "icgo"
                or structure_type == "icsp"
                or structure_type == "logS"
                or structure_type == "lg1S"
                or structure_type == "lssp"
                or structure_type == "modD"
                or structure_type == "moDD"
                or structure_type == "phyS"
                or structure_type == "ph1S"
            ):
                skip = 8
            elif structure_type == "blob":
                blen, = struct.unpack_from(">I", self.offset_read(4))
                skip = blen
            elif (
                structure_type == "ustr"
                or structure_type == "cmmt"
                or structure_type == "extn"
                or structure_type == "GRP0"
            ):
                blen, = struct.unpack_from(">I", self.offset_read(4))
                skip = 2 * blen
            elif structure_type == "BKGD":
                skip = 12
            elif (
                structure_type == "ICVO"
                or structure_type == "LSVO"
                or structure_type == "dscl"
            ):
                skip = 1
            elif structure_type == "Iloc" or structure_type == "fwi0":
                skip = 16
            elif structure_type == "dilc":
                skip = 32
            elif structure_type == "lsvo":
                skip = 76
            elif structure_type == "icvo":
                pass
            elif structure_type == "info":
                pass
            else:
                pass

            if skip <= 0:
                # We somehow didn't find a matching type. Maybe this file name's length value is broken. Try to fix it!
                # This is a bit voodoo and probably not the nicest way. Beware, there by dragons!
                self._log("Re-reading!")
                # Rewind 8 bytes, so that we can re-read structure_id and structure_type
                self.skip(-1 * 2 * 0x4)
                filename += self.offset_read(0x2).decode("utf-16be")
                # re-read structure_id and structure_type
                structure_id, = struct.unpack_from(">I", self.offset_read(4))
                structure_type, = struct.unpack_from(">4s", self.offset_read(4))
                structure_type = structure_type.decode()
                # Look-ahead and check if we have  structure_type==Iloc followed by blob.
                # If so, we're interested in blob, not Iloc. Otherwise continue!
                future_structure_type = struct.unpack_from(
                    ">4s", self.offset_read(4, offset=self.pos)
                )
                self._log(
                    "Re-read structure_id {} / structure_type {}".format(
                        structure_id, structure_type
                    )
                )
                if structure_type != "blob" and future_structure_type != "blob":
                    structure_type = ""
                    self._log("Forcing another round!")

        # Skip bytes until the next (file name) block
        self.skip(skip)
        self._log("Filename {}".format(filename))
        return filename

    def _log(self, *args):
        if self.debug:
            print("[DEBUG] {}".format(*args))


class DS_Store(DataBlock, object):
    """
    Represents the .DS_Store file from the given binary data. 
    """

    def __init__(self, data, debug=False):
        super(DS_Store, self).__init__(data, debug)
        self.data = data
        self.root = self.__read_header()
        self.offsets = self.__read_offsets()
        self.toc = self.__read_TOC()
        self.freeList = self.__read_freelist()
        self.debug = debug

    def __read_header(self):
        """
        Checks if self.data is actually a .DS_Store file by checking the magic bytes.
        It returns the file's root block.
        """
        # We read at least 32+4 bytes for the header!
        if len(self.data) < 36:
            raise ParsingError("Length of data is too short!")

        # Check the magic bytes for .DS_Store
        magic1, magic2 = struct.unpack_from(">II", self.offset_read(2 * 4))
        if not magic1 == 0x1 and not magic2 == 0x42756431:
            raise ParsingError("Magic byte 1 does not match!")

        # After the magic bytes, the offset follows two times with block's size in between.
        # Both offsets have to match and are the starting point of the root block
        offset, size, offset2 = struct.unpack_from(">III", self.offset_read(3 * 4))
        self._log("Offset 1: {}".format(offset))
        self._log("Size: {}".format(size))
        self._log("Offset 2: {}".format(offset2))
        if not offset == offset2:
            raise ParsingError("Offsets do not match!")
        # Skip 16 bytes of unknown data...
        self.skip(4 * 4)

        return DataBlock(self.offset_read(size, offset + 4), debug=self.debug)

    def __read_offsets(self):
        """
        Reads the offsets which follow the header.
        """
        start_pos = self.root.pos
        # First get the number of offsets in this file.
        count, = struct.unpack_from(">I", self.root.offset_read(4))
        self._log("Offset count: {}".format(count))
        # Always appears to be zero!
        self.root.skip(4)

        # Iterate over the offsets and get the offset addresses.
        offsets = []
        for i in range(count):
            # Address of the offset.
            address, = struct.unpack_from(">I", self.root.offset_read(4))
            self._log("Offset {} is {}".format(i, address))
            if address == 0:
                # We're only interested in non-zero values
                continue
            offsets.append(address)

        # Calculate the end of the address space (filled with zeroes) instead of dumbly reading zero values...
        section_end = start_pos + (count // 256 + 1) * 256 * 4 - count * 4

        # Skip to the end of the section
        self.root.skip(section_end)
        self._log(
            "Skipped {} to {}".format(
                hex(self.root.pos + section_end), hex(self.root.pos)
            )
        )
        self._log("Offsets: {}".format(offsets))
        return offsets

    def __read_TOC(self):
        """
        Reads the table of contents (TOCs) from the file.
        """
        self._log("POS {}".format(hex(self.root.pos)))
        # First get the number of ToC entries.
        count, = struct.unpack_from(">I", self.root.offset_read(4))
        self._log("Toc count: {}".format(count))
        toc = {}
        # Iterate over all ToCs
        for i in range(count):
            # Get the length of a ToC's name
            toc_len, = struct.unpack_from(">b", self.root.offset_read(1))
            # Read the ToC's name
            toc_name, = struct.unpack_from(
                ">{}s".format(toc_len), self.root.offset_read(toc_len)
            )
            # Read the address (block id) in the data section
            block_id, = struct.unpack_from(">I", self.root.offset_read(4))
            # Add all values to the dictionary
            toc[toc_name.decode()] = block_id

        self._log("Toc {}".format(toc))
        return toc

    def __read_freelist(self):
        """
        Read the free list from the header.
        The free list has n=0..31 buckets with the index 2^n
        """
        freelist = {}
        for i in range(32):
            freelist[2 ** i] = []
            # Read the amount of blocks in the specific free list.
            blkcount, = struct.unpack_from(">I", self.root.offset_read(4))
            for j in range(blkcount):
                # Read blkcount block offsets.
                free_offset, = struct.unpack_from(">I", self.root.offset_read(4))
                freelist[2 ** i].append(free_offset)

        self._log("Freelist: {}".format(freelist))
        return freelist

    def __block_by_id(self, block_id):
        """
        Create a DataBlock from a given block ID (e.g. from the ToC)
        """
        # First check if the block_id is within the offsets range
        if len(self.offsets) < block_id:
            raise ParsingError("BlockID out of range!")

        # Get the address of the block
        addr = self.offsets[block_id]

        # Do some necessary bit operations to extract the offset and the size of the block.
        # The address without the last 5 bits is the offset in the file
        offset = int(addr) >> 0x5 << 0x5
        # The address' last five bits are the block's size.
        size = 1 << (int(addr) & 0x1F)
        self._log(
            "New block: addr {} offset {} size {}".format(addr, offset + 0x4, size)
        )
        # Return the new block
        return DataBlock(self.offset_read(size, offset + 0x4), debug=self.debug)

    def traverse_root(self):
        """
        Traverse from the root block and extract all file names.
        """
        # Get the root block from the ToC 'DSDB'
        root = self.__block_by_id(self.toc["DSDB"])
        # Read the following root block's ID, so that we can traverse it.
        root_id, = struct.unpack(">I", root.offset_read(4))
        self._log("Root-ID ", root_id)

        # Read other values that we might be useful, but we're not interested in... (at least right now)
        internal_block_count, = struct.unpack(">I", root.offset_read(4))
        record_count, = struct.unpack(">I", root.offset_read(4))
        block_count, = struct.unpack(">I", root.offset_read(4))
        unknown, = struct.unpack(">I", root.offset_read(4))

        # traverse from the extracted root block id.
        return self.traverse(root_id)

    def traverse(self, block_id):
        """
        Traverses a block identified by the given block_id and extracts the file names.
        """
        # Get the responsible block by it's ID
        node = self.__block_by_id(block_id)
        # Extract the pointer to the next block
        next_pointer, = struct.unpack(">I", node.offset_read(4))
        # Get the number of next blocks or records
        count, = struct.unpack(">I", node.offset_read(4))
        self._log("Next Ptr {} with {} ".format(hex(next_pointer), hex(count)))

        filenames = []
        # If a next_pointer exists (>0), iterate through the next blocks recursively
        # If not, we extract all file names from the current block
        if next_pointer > 0:
            for i in range(0, count, 1):
                # Get the block_id for the next block
                next_id, = struct.unpack(">I", node.offset_read(4))
                self._log("Child: {}".format(next_id))
                # Traverse it recursively
                files = self.traverse(next_id)
                filenames += files
                # Also get the filename for the current block.
                filename = node.read_filename()
                self._log("Filename: ", filename)
                filenames.append(filename)
            # Now that we traversed all childs of the next_pointer, traverse the pointer itself.
            # TODO: Check if that is really necessary as the last child should be the current node... (or so?)
            files = self.traverse(next_pointer)
            filenames += files
        else:
            # We're probably in a leaf node, so extract the file names.
            for i in range(0, count, 1):
                f = node.read_filename()
                filenames.append(f)

        return filenames
